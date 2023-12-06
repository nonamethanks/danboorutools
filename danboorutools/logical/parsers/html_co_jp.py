from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.html_co_jp import HtmlCoJpArtistUrl


class HtmlCoJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> HtmlCoJpArtistUrl | None:
        match parsable_url.url_parts:
            case username, :
                return HtmlCoJpArtistUrl(parsed_url=parsable_url,
                                         username=username)
            case _:
                return None
