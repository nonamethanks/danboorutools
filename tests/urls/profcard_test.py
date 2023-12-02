import pytest

from danboorutools.logical.urls.profcard import ProfcardUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_info_test

urls = {
    ProfcardUrl: {
        "https://profcard.info/u/73eXlzsmfbXKmCjqJo4SeyNE2SN2": "https://profcard.info/u/73eXlzsmfbXKmCjqJo4SeyNE2SN2",
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
    generate_info_test(
        url_string="https://profcard.info/u/73eXlzsmfbXKmCjqJo4SeyNE2SN2",
        url_type=ProfcardUrl,
        url_properties=dict(user_id="73eXlzsmfbXKmCjqJo4SeyNE2SN2"),
        primary_names=["巴"],
        secondary_names=[],
        related=["https://poipiku.com/609078/"],
    )
