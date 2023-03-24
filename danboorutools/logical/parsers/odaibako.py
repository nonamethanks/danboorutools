from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.odaibako import OdaibakoUrl


class OdaibakoNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> OdaibakoUrl | None:
        match parsable_url.url_parts:
            case "u", username:
                instance = OdaibakoUrl(parsable_url)
                instance.username = username
            case _:
                return None

        return instance
