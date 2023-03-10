from danboorutools.logical.extractors.pixiv import PixivMeUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class PixivMeParser(UrlParser):
    test_cases = {
        PixivMeUrl: [
            "http://www.pixiv.me/noizave"
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PixivMeUrl | None:
        match parsable_url.url_parts:
            case stacc, :
                instance = PixivMeUrl(parsable_url)
                instance.stacc = stacc
            case _:
                return None
        return instance
