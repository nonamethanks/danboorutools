import pytest

from danboorutools.logical.urls.privatter import PrivatterArtistUrl, PrivatterImageUrl, PrivatterPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl, _TestPostUrl

urls = {
    PrivatterPostUrl: {
        "http://privatter.net/p/8096124": "https://privatter.net/p/8096124",
        "http://privatter.net/i/2655076": "https://privatter.net/i/2655076",
    },
    PrivatterArtistUrl: {
        "https://privatter.net/u/uzura_55": "https://privatter.net/u/uzura_55",
        "https://privatter.net/m/naoaraaa04": "https://privatter.net/u/naoaraaa04",
    },
    PrivatterImageUrl: {
        "http://privatter.net/img_original/856121876520129d361c6e.jpg": "http://privatter.net/img_original/856121876520129d361c6e.jpg",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestPrivatterArtistUrl(_TestArtistUrl):
    url_string = "https://privatter.net/u/uzura_55"
    url_type = PrivatterArtistUrl
    url_properties = dict(username="uzura_55")
    primary_names = []
    secondary_names = ["uzura_55"]
    related = ["https://www.twitter.com/uzura_55"]


class TestPrivatterPostUrl(_TestPostUrl):
    url_string = "http://privatter.net/p/8096124"
    url_type = PrivatterPostUrl
    url_properties = dict(post_id=8096124, post_type="p")
    gallery = "https://privatter.net/u/uzura_55"
