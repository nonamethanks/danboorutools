
from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.anifty import AniftyImageUrl, AniftyUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class ImgixNetParser(UrlParser):
    test_cases = {
        AniftyImageUrl: [
            "https://anifty.imgix.net/creation/0x961d09077b4a9f7a27f6b7ee78cb4c26f0e72c18/20d5ce5b5163a71258e1d0ee152a0347bf40c7da.png?w=660&h=660&fit=crop&crop=focalpoint&fp-x=0.76&fp-y=0.5&fp-z=1&auto=compress",
            "https://anifty.imgix.net/creation/0x961d09077b4a9f7a27f6b7ee78cb4c26f0e72c18/48b1409838cf7271413480b8533372844b9f2437.png?w=3840&q=undefined&auto=compress",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AniftyUrl | None:
        if parsable_url.subdomain == "anifty":
            return cls._match_anifty(parsable_url)
        else:
            raise UnparsableUrl(parsable_url.url)

    @staticmethod
    def _match_anifty(parsable_url: ParsableUrl) -> AniftyUrl | None:
        match parsable_url.url_parts:
            case _, artist_hash, _ if artist_hash.startswith("0x"):
                instance = AniftyImageUrl(parsable_url.url)
                instance.artist_hash = artist_hash
            case _:
                return None

        return instance
