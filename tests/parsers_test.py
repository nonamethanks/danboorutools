from ward import test

from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.logical.parsers import UrlParser, parsers
from danboorutools.models.url import Url


def spawn_url_parsing_test(url_string: str, url_type: type[Url]) -> None:
    domain = ParsableUrl(url_string).domain

    @test(f"Parsing {domain}: {url_string}", tags=["parsing", domain])
    def _(url_string=url_string, url_type=url_type) -> None:
        parsed_url = UrlParser.parse(url_string)
        assert isinstance(parsed_url, url_type)


for parser in parsers.values():
    for _url, _url_type in [(url, url_type) for url_type, url_group in parser.test_cases.items() for url in url_group]:
        spawn_url_parsing_test(_url, _url_type)
