from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.bitly import BitlyUrl


class BitLyParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> BitlyUrl | None:
        match parsable_url.url_parts:
            case redirect_id, :
                return BitlyUrl(parsed_url=parsable_url,
                                redirect_id=redirect_id)

            case _:
                return None
