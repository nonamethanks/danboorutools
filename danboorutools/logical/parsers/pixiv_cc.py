from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.pixiv import PixivStaccUrl


class PixivCcParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PixivStaccUrl | None:
        match parsable_url.url_parts:
            case stacc, *_:
                return PixivStaccUrl(parsed_url=parsable_url,
                                     stacc=stacc)

            case _:
                return None
