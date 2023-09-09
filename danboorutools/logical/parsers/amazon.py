from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.amazon import AmazonAuthorUrl, AmazonItemUrl, AmazonShortenerUrl, AmazonUrl
from danboorutools.logical.urls.enty import EntyImageUrl
from danboorutools.logical.urls.skeb import SkebImageUrl
from danboorutools.models.url import UselessUrl

RESERVED_NAMES = {"blogs", "en", "messages", "posts", "products", "ranking",
                  "search", "series", "service_navigations", "signout", "titles", "users"}


class AmazonawsComParser(UrlParser):
    test_cases = {
        EntyImageUrl: [
            "https://entyjp.s3-ap-northeast-1.amazonaws.com/uploads/post/attachment/141598/20211227_130_030_100.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIMO6YQGDXLXXJKQA%2F20221224%2Fap-northeast-1%2Fs3%2Faws4_request&X-Amz-Date=20221224T235529Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=42857026422339a2ba9ea362d91e2b34cc0718fbeee529166e8bfa80f757bb94",
        ],
        SkebImageUrl: [
            "https://skeb-production.s3.ap-northeast-1.amazonaws.com/uploads/outputs/20f9d68f-50ec-44ae-8630-173fc38a2d6a?response-content-disposition=attachment%3B%20filename%3D%22458093-1.output.mp4%22%3B%20filename%2A%3DUTF-8%27%27458093-1.output.mp4&response-content-type=video%2Fmp4&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIVPUTFQBBL7UDSUA%2F20220221%2Fap-northeast-1%2Fs3%2Faws4_request&X-Amz-Date=20220221T200057Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=7f028cfd9a56344cf1d42410063fad3ef30a1e47b83cef047247e0c37df01df0",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> EntyImageUrl | SkebImageUrl | None:
        if parsable_url.hostname == "entyjp.s3-ap-northeast-1.amazonaws.com":
            return cls._match_enty(parsable_url)
        elif parsable_url.hostname == "skeb-production.s3.ap-northeast-1.amazonaws.com":
            return cls._match_skeb(parsable_url)
        else:
            raise UnparsableUrlError(parsable_url)

    @staticmethod
    def _match_enty(parsable_url: ParsableUrl) -> EntyImageUrl | None:
        match parsable_url.url_parts:
            case "uploads", "post", "attachment", post_id, _:
                return EntyImageUrl(parsed_url=parsable_url,
                                    post_id=int(post_id))

            case _:
                return None

    @staticmethod
    def _match_skeb(parsable_url: ParsableUrl) -> SkebImageUrl | None:
        match parsable_url.url_parts:
            case "uploads", "outputs", image_uuid:
                return SkebImageUrl(parsed_url=parsable_url,
                                    image_uuid=image_uuid,
                                    page=None,
                                    post_id=None)
            case _:
                return None


class AmazonComParser(UrlParser):
    domains = ["amazon.com", "amazon.jp"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AmazonUrl | UselessUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case "hz", "wishlist", "ls", _wishlist_id:
                return UselessUrl(parsed_url=parsable_url)
            case "gp", "registry", "wishlist", _wishlist_id:
                return UselessUrl(parsed_url=parsable_url)

            case _ if parsable_url.subdomain not in ["www", ""]:
                raise UnparsableUrlError(parsable_url)

            # https://www.amazon.com/dp/B08BWGQ8NP/
            # https://www.amazon.com/Yaoi-Hentai-2/dp/1933664010
            case *_, "dp", item_id:
                return AmazonItemUrl(parsed_url=parsable_url,
                                     item_id=item_id,
                                     subsite=parsable_url.tld)

            # https://amazon.jp/o/ASIN/B000P29X0G/ref=nosim/conoco-22
            case "o", "ASIN", item_id, *_:
                return AmazonItemUrl(parsed_url=parsable_url,
                                     item_id=item_id,
                                     subsite=parsable_url.tld)

            # https://www.amazon.com/exec/obidos/ASIN/B004U99O9K/ref=nosim/accessuporg-20?SubscriptionId=1MNS6Z3H8Y5Q5XCMG582\u0026linkCode=xm2\u0026creativeASIN=B004U99O9K
            case "exec", "obidos", "ASIN", item_id, *_:
                return AmazonItemUrl(parsed_url=parsable_url,
                                     item_id=item_id,
                                     subsite=parsable_url.tld)

            # https://www.amazon.com/gp/product/B08CTJWTMR
            case "gp", "product", item_id:
                return AmazonItemUrl(parsed_url=parsable_url,
                                     item_id=item_id,
                                     subsite=parsable_url.tld)

            # https://www.amazon.com/Shei-Darksbane/e/B0127EHZ7W/
            case _display_name, "e", author_id:
                return AmazonAuthorUrl(parsed_url=parsable_url,
                                       author_id=author_id,
                                       subsite=parsable_url.tld)

            # https://www.amazon.com/stores/Shei-Darksbane/author/B0127EHZ7W
            case "stores", _display_name, "author", author_id:
                return AmazonAuthorUrl(parsed_url=parsable_url,
                                       author_id=author_id,
                                       subsite=parsable_url.tld)

            # https://www.amazon.com/stores/author/B0127EHZ7W
            case "stores", "author", author_id:
                return AmazonAuthorUrl(parsed_url=parsable_url,
                                       author_id=author_id,
                                       subsite=parsable_url.tld)

            case _, "s":
                raise UnparsableUrlError(parsable_url)

            case _:
                return None


class AmazonShortener(UrlParser):
    domains = ["amzn.to", "amzn.asia"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AmazonShortenerUrl | None:
        match parsable_url.url_parts:
            case shortener_id, :
                return AmazonShortenerUrl(parsed_url=parsable_url,
                                          shortener_id=shortener_id)

            case _:
                return None
