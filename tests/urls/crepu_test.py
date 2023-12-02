import pytest

from danboorutools.logical.urls.crepu import CrepuArtistUrl, CrepuPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    CrepuArtistUrl: {
        "https://crepu.net/user/shio_332": "https://crepu.net/user/shio_332",
    },
    CrepuPostUrl: {
        "https://crepu.net/post/264943": "https://crepu.net/post/264943",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_artist_url_1():
    generate_artist_test(
        url_string="https://crepu.net/user/shio_332",
        url_type=CrepuArtistUrl,
        url_properties=dict(username="shio_332"),
        primary_names=["汐見"],
        secondary_names=["shio_332"],
        related=["https://twitter.com/nomiya332", "https://www.pixiv.net/users/87958749", "https://xfolio.jp/portfolio/nomiya332"],
    )
