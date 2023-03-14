import re

from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.circle_ms import CircleMsCircleUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.models.url import UselessUrl


class CircleMsParser(UrlParser):
    id_subdomain = re.compile(r"^c(\d+)$")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> CircleMsCircleUrl | UselessUrl | None:
        match parsable_url.url_parts:
            # https://portal.circle.ms/Circle/Index/10315665
            # http://portal.circle.ms/circle/index/10022032/
            case ("Circle" | "circle"), ("Index" | "index"), circle_id if parsable_url.subdomain == "portal":
                instance = CircleMsCircleUrl(parsable_url)
                instance.circle_id = int(circle_id)

            # http://webcatalog.circle.ms/Perma/Circle/10217247
            case "Perma", "Circle", circle_id if parsable_url.subdomain.startswith("webcatalog"):
                instance = CircleMsCircleUrl(parsable_url)
                instance.circle_id = int(circle_id)

            # https://webcatalog-free.circle.ms/Circle/14232303
            case "Circle", circle_id if parsable_url.subdomain.startswith("webcatalog"):
                instance = CircleMsCircleUrl(parsable_url)
                instance.circle_id = int(circle_id)

            # http://c10011401.circle.ms/oc/CircleProfile.aspx
            # http://c10067422.circle.ms/cr/CircleProfile.aspx
            # http://c10024411.circle.ms/cr/CircleHome.aspx
            # http://c10025912.circle.ms/oc/CircleImages.aspx
            # http://c10003509.circle.ms/oc/circleprofile.aspx
            # http://c10014108.circle.ms/pics.aspx?PCODE=566388-04-1\u0026PTHUMB=false
            # http://c10001034.circle.ms/oc/pp/Paper.aspx?CPID=12505
            case *_, asp_page if asp_page.endswith(".aspx") and cls.id_subdomain.match(parsable_url.subdomain):
                instance = CircleMsCircleUrl(parsable_url)
                instance.circle_id = int(parsable_url.subdomain.removeprefix("c"))

            # http://myportal.circle.ms/CircleInfo/Menu/10251988
            case "CircleInfo", "Menu", circle_id:
                instance = CircleMsCircleUrl(parsable_url)
                instance.circle_id = int(circle_id)

            # http://p10001378.circle.ms/tu/Pixiv.aspx
            case _, "Pixiv.aspx":
                raise UnparsableUrl(parsable_url)

            # http://p10011607.circle.ms/st/Profile.aspx
            # http://p10035738.circle.ms/ps/Profile.aspx
            case _, "Profile.aspx":
                raise UnparsableUrl(parsable_url)

            case "assets", "images", _, _:  # various site assets
                raise UnparsableUrl(parsable_url)

            case [] if parsable_url.subdomain.startswith("webcatalog"):
                return UselessUrl(parsable_url)

            case [] if parsable_url.subdomain in ["auth2"]:
                return UselessUrl(parsable_url)

            case _:
                return None

        return instance
