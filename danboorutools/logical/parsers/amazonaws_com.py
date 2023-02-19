from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.enty import EntyImageUrl, EntyUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser

RESERVED_NAMES = ["blogs", "en", "messages", "posts", "products", "ranking",
                  "search", "series", "service_navigations", "signout", "titles", "users"]


class AmazonawsComParser(UrlParser):
    test_cases = {
        EntyImageUrl: [
            "https://entyjp.s3-ap-northeast-1.amazonaws.com/uploads/post/attachment/141598/20211227_130_030_100.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIMO6YQGDXLXXJKQA%2F20221224%2Fap-northeast-1%2Fs3%2Faws4_request&X-Amz-Date=20221224T235529Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=42857026422339a2ba9ea362d91e2b34cc0718fbeee529166e8bfa80f757bb94",

        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> EntyUrl | None:
        if parsable_url.hostname == "entyjp.s3-ap-northeast-1.amazonaws.com":
            instance = EntyImageUrl(parsable_url)
            instance.post_id = int(parsable_url.url_parts[3])
        else:
            raise UnparsableUrl(parsable_url)

        return instance
