from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.pixiv import PixivMeUrl


class PixivMeParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PixivMeUrl | None:
        match parsable_url.url_parts:
            case stacc, :
                return PixivMeUrl(parsed_url=parsable_url,
                                  stacc=stacc)

            case _:
                return None
