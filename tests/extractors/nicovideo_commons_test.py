
from ward import test

from danboorutools.models.url import Url

urls = {
    "https://commons.nicovideo.jp/user/696839": "https://commons.nicovideo.jp/user/696839",

    "https://commons.nicovideo.jp/material/nc138051": "https://commons.nicovideo.jp/material/nc138051",
    "https://deliver.commons.nicovideo.jp/thumbnail/nc285306?size=ll": "https://commons.nicovideo.jp/material/nc285306",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
