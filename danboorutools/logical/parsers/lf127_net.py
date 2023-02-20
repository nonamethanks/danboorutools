from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.lofter import LofterImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class Lf127NetParser(UrlParser):
    domains = ["lf127.net", "127.net"]

    test_cases = {
        LofterImageUrl: [
            "https://imglf3.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJSzFCWFlnUWgzb01DcUdpT1lreG5yQjJVMkhGS09HNGR3PT0.png?imageView&thumbnail=1680x0&quality=96&stripmeta=0",
            "https://imglf3.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJSzFCWFlnUWgzb01DcUdpT1lreG5yQjJVMkhGS09HNGR3PT0.png",
            "http://imglf0.nosdn.127.net/img/cHl3bXNZdDRaaHBnNWJuN1Y4OXBqR01CeVBZSVNmU2FWZWtHc1h4ZTZiUGxlRzMwZnFDM1JnPT0.jpg",  # (404)
            # "http://gacha.nosdn.127.net/0a47df61008b46668a56d2f9e4b3c0b3.png?axis=0\u0026enlarge=1\u0026imageView\u0026quality=100\u0026type=png",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> LofterImageUrl | None:
        match parsable_url.url_parts:
            case "img", _:
                instance = LofterImageUrl(parsable_url)
            case [_]:
                raise UnparsableUrl(parsable_url)
            case _:
                return None

        return instance
