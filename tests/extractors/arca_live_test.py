# pylint: disable=cell-var-from-loop
from ward import test

from danboorutools.models.url import Url

urls = {
    "https://arca.live/b/arknights/66031722": "https://arca.live/b/arknights/66031722",
    "https://arca.live/u/@Si리링": "https://arca.live/u/@Si리링",
    "https://arca.live/u/@Nauju/45320365": "https://arca.live/u/@Nauju/45320365",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
