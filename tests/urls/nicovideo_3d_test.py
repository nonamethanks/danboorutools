import pytest

from danboorutools.logical.urls import nicovideo_3d as n3
from tests.helpers.parsing import generate_parsing_test

urls = {
    n3.Nicovideo3dArtistUrl: {
        "https://3d.nicovideo.jp/users/109584": "https://3d.nicovideo.jp/users/109584",
        "https://3d.nicovideo.jp/users/29626631/works": "https://3d.nicovideo.jp/users/29626631",
        "https://3d.nicovideo.jp/u/siobi": "https://3d.nicovideo.jp/u/siobi",
    },
    n3.Nicovideo3dPostUrl: {
        "https://3d.nicovideo.jp/works/td28606": "https://3d.nicovideo.jp/works/td28606",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
