from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.peing import PeingUrl, PeingUserUrl


class PeingNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PeingUrl | None:
        match parsable_url.url_parts:
            case username, if username != "me":
                return PeingUserUrl(parsed_url=parsable_url,
                                    username=username)
            case lang, username if lang in ("ko", "ja", "en", "zh-TW", "zh-CN") and username != "me":
                return PeingUserUrl(parsed_url=parsable_url,
                                    username=username)
            case _:
                return None
