# pylint: disable=cell-var-from-loop
from ward import test

from danboorutools.models.url import Url

urls = {
    "https://anifty.jp/creations/373": "https://anifty.jp/creations/373",
    "https://anifty.jp/ja/creations/373": "https://anifty.jp/creations/373",
    "https://anifty.jp/zh/creations/373": "https://anifty.jp/creations/373",
    "https://anifty.jp/zh-Hant/creations/373": "https://anifty.jp/creations/373",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
