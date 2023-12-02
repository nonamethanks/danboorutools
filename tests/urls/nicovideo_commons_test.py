import pytest

from danboorutools.logical.urls import nicovideo_commons as nc
from tests.helpers.parsing import generate_parsing_test

urls = {
    nc.NicovideoCommonsArtistUrl: {
        "https://commons.nicovideo.jp/user/696839": "https://commons.nicovideo.jp/user/696839",
    },
    nc.NicovideoCommonsPostUrl: {
        "https://commons.nicovideo.jp/material/nc138051": "https://commons.nicovideo.jp/material/nc138051",
        "https://deliver.commons.nicovideo.jp/thumbnail/nc285306?size=ll": "https://commons.nicovideo.jp/material/nc285306",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
