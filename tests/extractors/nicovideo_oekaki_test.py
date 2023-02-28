
from ward import test

from danboorutools.models.url import Url

urls = {
    "https://dic.nicovideo.jp/oekaki/176310.png": "https://dic.nicovideo.jp/oekaki/176310.png",

    "https://dic.nicovideo.jp/oekaki_id/340604": "https://dic.nicovideo.jp/oekaki_id/340604",

    "https://dic.nicovideo.jp/u/11141663": "https://dic.nicovideo.jp/u/11141663",
    "https://dic.nicovideo.jp/r/u/10846063/2063955": "https://dic.nicovideo.jp/u/10846063",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
