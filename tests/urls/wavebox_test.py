import pytest

from danboorutools.logical.urls.wavebox import WaveboxUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    WaveboxUrl: {
        "https://wavebox.me/wave/c5c9yndqm26x5l6f/": "https://wavebox.me/wave/c5c9yndqm26x5l6f/",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestVkArtistUrl(_TestArtistUrl):
    url_string = "https://wavebox.me/wave/230rwk0rodc71cu6/"
    url_type = WaveboxUrl
    url_properties = dict(user_id="230rwk0rodc71cu6")
    primary_names = ["甘粥"]
    secondary_names = []
    related = []
