import pytest

from danboorutools.logical.urls.peing import PeingUserUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    PeingUserUrl: {
        "https://peing.net/ko/rhlg11": "https://peing.net/rhlg11",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestPeingUserUrl(_TestArtistUrl):
    url_string = "https://peing.net/en/dank0ng"
    url_type = PeingUserUrl
    url_properties = dict(username="dank0ng")
    primary_names = ["단콩"]
    secondary_names = ["dank0ng"]
    related = []
