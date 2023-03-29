from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.twpf import TwpfUrl


class TwpfJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> TwpfUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case username, if username not in ("about", "search", "signup", "login"):
                return TwpfUrl(parsed_url=parsable_url,
                               username=username)

            case _:
                return None
