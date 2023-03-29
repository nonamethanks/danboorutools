from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.carrd import CarrdUrl


class CarrdCoParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> CarrdUrl | None:
        return CarrdUrl(parsed_url=parsable_url,
                        username=parsable_url.subdomain)
