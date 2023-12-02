import pytest

from danboorutools.logical.urls.bcy import BcyArtistUrl, BcyPostUrl, OldBcyPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    BcyArtistUrl: {
        "https://bcy.net/u/2825982/like": "https://bcy.net/u/2825982",
    },
    BcyPostUrl: {
        "https://bcy.net/item/detail/6576655701886632206?_source_page=": "https://bcy.net/item/detail/6576655701886632206",
    },
    OldBcyPostUrl: {
        "http://bcy.net/illust/detail/9988/801318": "https://bcy.net/illust/detail/9988/801318",
        "https://bcy.net/illust/detail/158436": "https://bcy.net/illust/detail/158436",
        "https://bcy.net/coser/detail/89784": "https://bcy.net/illust/detail/89784",
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
    generate_artist_test(
        url_string="https://bcy.net/u/2825982",
        url_type=BcyArtistUrl,
        url_properties=dict(user_id=2825982),
        primary_names=[],
        secondary_names=[],
        related=[],
        is_deleted=True,
    )
