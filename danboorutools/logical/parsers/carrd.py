from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.carrd import CarrdUrl


class CarrdCoParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> CarrdUrl | None:
        instance = CarrdUrl(parsable_url)
        instance.username = parsable_url.subdomain
        return instance
