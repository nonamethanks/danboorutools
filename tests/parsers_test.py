from ward import test

from danboorutools.logical.parsers import UrlParser, parsers
from danboorutools.models.url import Url


def spawn_url_test(url_string: str, url_type: type[Url]) -> None:
    @test(f"Parsing url {url_string}", tags=["parsing"])
    def _(_url: str = url_string, _url_type: type[Url] = url_type) -> None:
        parsed_url = UrlParser.parse(_url)
        assert isinstance(parsed_url, _url_type)


for parser in parsers.values():
    for url, url_type in [(url, url_type) for url_type, url_group in parser.test_cases.items() for url in url_group]:
        spawn_url_test(url, url_type)
