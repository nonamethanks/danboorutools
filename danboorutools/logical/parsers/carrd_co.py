from danboorutools.logical.extractors.carrd import CarrdUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class CarrdCoParser(UrlParser):
    test_cases = {
        CarrdUrl: [
            "https://veriea.carrd.co/"
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> CarrdUrl | None:
        instance = CarrdUrl(parsable_url)
        assert parsable_url.subdomain
        instance.username = parsable_url.subdomain
        return instance
