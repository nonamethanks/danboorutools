from danboorutools.logical.extractors.bitly import BitlyUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class BitLyParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> BitlyUrl | None:
        match parsable_url.url_parts:
            case redirect_id, :
                instance = BitlyUrl(parsable_url)
                instance.redirect_id = redirect_id
            case _:
                return None

        return instance
