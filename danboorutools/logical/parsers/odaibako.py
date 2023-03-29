from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.odaibako import OdaibakoUrl


class OdaibakoNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> OdaibakoUrl | None:
        match parsable_url.url_parts:
            case "u", username:
                return OdaibakoUrl(parsed_url=parsable_url,
                                   username=username)

            case _:
                return None
