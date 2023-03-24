from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.lofter import LofterArtistUrl, LofterImageUrl, LofterPostUrl, LofterUrl


class LofterComParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> LofterUrl | None:
        instance: LofterUrl
        if parsable_url.subdomain in ["www", "i", ""]:
            match parsable_url.url_parts:
                # http://www.lofter.com/app/xiaokonggedmx
                # http://www.lofter.com/blog/semblance
                case ("app" | "blog"), username:
                    instance = LofterArtistUrl(parsable_url)
                    instance.username = username

                # https://www.lofter.com/front/blog/home-page/noshiqian
                case "front", "blog", "home-page", username:
                    instance = LofterArtistUrl(parsable_url)
                    instance.username = username

                case _:
                    return None
        else:
            match parsable_url.url_parts:
                # https://gengar563.lofter.com/post/1e82da8c_1c98dae1b
                case "post", post_id:
                    instance = LofterPostUrl(parsable_url)
                    instance.username = parsable_url.subdomain
                    instance.post_id = post_id

                # http://gengar563.lofter.com
                case _:
                    instance = LofterArtistUrl(parsable_url)
                    instance.username = parsable_url.subdomain

        return instance


class Lf127NetParser(UrlParser):
    domains = ["lf127.net", "127.net"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> LofterImageUrl | None:
        match parsable_url.url_parts:
            # https://imglf3.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJSzFCWFlnUWgzb01DcUdpT1lreG5yQjJVMkhGS09HNGR3PT0.png?imageView&thumbnail=1680x0&quality=96&stripmeta=0
            # https://imglf3.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJSzFCWFlnUWgzb01DcUdpT1lreG5yQjJVMkhGS09HNGR3PT0.png
            # http://imglf0.nosdn.127.net/img/cHl3bXNZdDRaaHBnNWJuN1Y4OXBqR01CeVBZSVNmU2FWZWtHc1h4ZTZiUGxlRzMwZnFDM1JnPT0.jpg
            # http://gacha.nosdn.127.net/0a47df61008b46668a56d2f9e4b3c0b3.png?axis=0\u0026enlarge=1\u0026imageView\u0026quality=100\u0026type=png
            case "img", _:
                instance = LofterImageUrl(parsable_url)
            case [_]:
                raise UnparsableUrlError(parsable_url)
            case _:
                return None

        return instance
