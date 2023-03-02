from danboorutools.logical.extractors.carrd import CarrdUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class CarrdCoParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> CarrdUrl | None:
        instance = CarrdUrl(parsable_url)
        instance.username = parsable_url.subdomain
        return instance
