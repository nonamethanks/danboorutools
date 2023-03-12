from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.enty import EntyImageUrl
from danboorutools.logical.extractors.skeb import SkebImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser
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
            raise UnparsableUrl(parsable_url)

    @staticmethod
    def _match_enty(parsable_url: ParsableUrl) -> EntyImageUrl | None:
        match parsable_url.url_parts:
            case "uploads", "post", "attachment", post_id, _:
                instance = EntyImageUrl(parsable_url)
                instance.post_id = int(post_id)
            case _:
                return None

        return instance

    @staticmethod
    def _match_skeb(parsable_url: ParsableUrl) -> SkebImageUrl | None:
        match parsable_url.url_parts:
            case "uploads", "outputs", image_uuid:
                instance = SkebImageUrl(parsable_url)
                instance.image_uuid = image_uuid
                instance.page = None
                instance.post_id = None
            case _:
                return None

        return instance


class AmazonComParser(UrlParser):
    domains = ["amazon.com", "amazon.jp"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> UselessUrl | None:
        match parsable_url.url_parts:
            case "hz", "wishlist", "ls", _wishlist_id:
                instance = UselessUrl(parsable_url)
            case _:
                return None

        return instance
