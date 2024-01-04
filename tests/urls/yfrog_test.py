import pytest

from danboorutools.logical.urls.yfrog import YfrogArtistUrl, YfrogImageUrl, YfrogPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    YfrogArtistUrl: {
        "http://yfrog.com/user/ponpoppo/photos": "http://yfrog.com/user/ponpoppo/photos",
    },
    YfrogPostUrl: {
        "http://yfrog.com/n4tgq2j": "http://yfrog.com/n4tgq2j",
    },
    YfrogImageUrl: {
        "http://a.yfrog.com/img593/7849/ljj7.jpg": "",
        "http://img571.yfrog.com/img571/9228/o64g.jpg": "",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestYfrogArtistUrl(_TestArtistUrl):
    url_string = "http://yfrog.com/user/ponpoppo/photos"
    url_type = YfrogArtistUrl
    url_properties = dict(username="ponpoppo")
    primary_names = []
    secondary_names = ["ponpoppo"]
    related = []
    is_deleted = True
