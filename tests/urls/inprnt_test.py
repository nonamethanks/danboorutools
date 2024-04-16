import pytest

from danboorutools.logical.urls.inprnt import InprntArtistUrl, InprntImageUrl, InprntPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    InprntArtistUrl: {
        "http://inprnt.com/gallery/keibleh": "https://www.inprnt.com/gallery/keibleh",
    },
    InprntPostUrl: {
        "https://www.inprnt.com/gallery/mizomei/karlach/": "https://www.inprnt.com/discover/image/mizomei/karlach",
    },
    InprntImageUrl: {
        "https://cdn.inprnt.com/thumbs/82/4c/824ce29bd4089dfb8a376919b3015063@2x.jpg": "https://cdn.inprnt.com/thumbs/82/4c/824ce29bd4089dfb8a376919b3015063@2x.jpg",
        "https://cdn.inprnt.com/thumbs/82/4c/824ce29bd4089dfb8a376919b3015063.jpg": "https://cdn.inprnt.com/thumbs/82/4c/824ce29bd4089dfb8a376919b3015063@2x.jpg",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestInprntArtistUrl(_TestArtistUrl):
    url_string = "https://www.inprnt.com/gallery/chuckart/"
    url_type = InprntArtistUrl
    url_properties = dict(username="chuckart")
    primary_names = []
    secondary_names = ["chuckart"]
    related = []
