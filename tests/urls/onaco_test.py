import pytest

from danboorutools.logical.urls.onaco import OnacoArtistUrl, OnacoImageUrl, OnacoPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    OnacoArtistUrl: {
        "https://onaco.jp/profile/paxmagellanic": "https://onaco.jp/profile/paxmagellanic",
    },
    OnacoPostUrl: {
        "https://onaco.jp/detail/ihkh6fx1bv71": "https://onaco.jp/detail/ihkh6fx1bv71",
    },
    OnacoImageUrl: {
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestOnacoArtistUrl(_TestArtistUrl):
    url_string = "https://onaco.jp/profile/paxmagellanic"
    url_type = OnacoArtistUrl
    url_properties = dict(username="paxmagellanic")
    primary_names = []
    secondary_names = ["paxmagellanic"]
    related = []
