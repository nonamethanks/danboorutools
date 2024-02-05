import pytest

from danboorutools.logical.urls.subscribestar import SubscribestarArtistUrl, SubscribestarPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    SubscribestarArtistUrl: {
        "https://subscribestar.adult/everyday2": "https://subscribestar.adult/everyday2",
    },
    SubscribestarPostUrl: {
        "https://subscribestar.adult/posts/437146": "https://subscribestar.adult/posts/437146",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestSubscribestarArtistUrl(_TestArtistUrl):
    url_string = "https://subscribestar.adult/everyday2"
    url_type = SubscribestarArtistUrl
    url_properties = dict(username="everyday2")
    primary_names = ["everyday2"]
    secondary_names = []
    related = []
