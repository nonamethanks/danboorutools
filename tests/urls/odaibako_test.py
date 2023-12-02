import pytest

from danboorutools.logical.urls.odaibako import OdaibakoUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_info_test

urls = {
    OdaibakoUrl: {
        "http://odaibako.net/u/kyou1999080": "https://odaibako.net/u/kyou1999080",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_info_url_1():
    generate_info_test(
        url_string="https://odaibako.net/u/kazahana__h",
        url_type=OdaibakoUrl,
        url_properties=dict(username="kazahana__h"),
        primary_names=["箱"],
        secondary_names=["kazahana__h"],
        related=["https://twitter.com/kazahana__h"],
    )


def test_info_url_2():
    generate_info_test(
        url_string="https://odaibako.net/u/mitumituami_",
        url_type=OdaibakoUrl,
        url_properties=dict(username="mitumituami_"),
        primary_names=["三ツ三ツ編ミ 🔞のお題箱"],
        secondary_names=["mitumituami_"],
        related=["https://twitter.com/mitumituami_"],
    )
