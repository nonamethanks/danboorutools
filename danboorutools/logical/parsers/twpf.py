from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.twpf import TwpfUrl


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
