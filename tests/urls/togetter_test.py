import pytest

from danboorutools.logical.urls.togetter import TogetterArtistUrl, TogetterLiUrl, TogetterPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    TogetterPostUrl: {
        "https://min.togetter.com/yF7scb6": "https://min.togetter.com/yF7scb6",
    },
    TogetterArtistUrl: {
        "https://min.togetter.com/id/srm_chi": "https://min.togetter.com/id/srm_chi",
    },
    TogetterLiUrl: {
        "https://togetter.com/li/107987": "https://togetter.com/li/107987",
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
        url_string="https://min.togetter.com/id/srm_chi",
        url_type=TogetterArtistUrl,
        url_properties=dict(username="srm_chi"),
        primary_names=[],
        secondary_names=["srm_chi"],
        related=["https://twitter.com/srm_chi"],
        is_deleted=True,
    )
