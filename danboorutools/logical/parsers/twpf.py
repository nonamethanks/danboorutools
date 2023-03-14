from danboorutools.logical.extractors.twpf import TwpfUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class TwpfJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> TwpfUrl | None:
        match parsable_url.url_parts:
            case username, if username not in ("about", "search", "signup", "login"):
                instance = TwpfUrl(parsable_url)
                instance.username = username
            case _:
                return None

        return instance
