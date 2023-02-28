
from ward import test

from danboorutools.models.url import Url

urls = {
    "https://3d.nicovideo.jp/users/109584": "https://3d.nicovideo.jp/users/109584",
    "https://3d.nicovideo.jp/users/29626631/works": "https://3d.nicovideo.jp/users/29626631",
    "https://3d.nicovideo.jp/u/siobi": "https://3d.nicovideo.jp/u/siobi",

    "https://3d.nicovideo.jp/works/td28606": "https://3d.nicovideo.jp/works/td28606",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
