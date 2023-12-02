import pytest

from danboorutools.logical.urls import nicovideo_oekaki as no
from tests.helpers.parsing import generate_parsing_test

urls = {
    no.NicovideoOekakiImageUrl: {
        "https://dic.nicovideo.jp/oekaki/176310.png": "https://dic.nicovideo.jp/oekaki/176310.png",
    },
    no.NicovideoOekakiPostUrl: {
        "https://dic.nicovideo.jp/oekaki_id/340604": "https://dic.nicovideo.jp/oekaki_id/340604",
    },
    no.NicovideoOekakiArtistUrl: {
        "https://dic.nicovideo.jp/u/11141663": "https://dic.nicovideo.jp/u/11141663",
        "https://dic.nicovideo.jp/r/u/10846063/2063955": "https://dic.nicovideo.jp/u/10846063",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
