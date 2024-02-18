import pytest

from danboorutools.logical.urls.carrd import CarrdUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestInfoUrl

urls = {
    CarrdUrl: {
        "https://veriea.carrd.co/": "https://veriea.carrd.co",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestCarrdUrl(_TestInfoUrl):
    url_string = "https://veriea.carrd.co"
    url_type = CarrdUrl
    url_properties = dict(username="veriea")
    primary_names = []
    secondary_names = ["veriea"]
    related = []
