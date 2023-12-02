import pytest

from danboorutools.logical.urls.taittsuu import TaittsuuArtistUrl, TaittsuuPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    TaittsuuArtistUrl: {
        "https://taittsuu.com/users/reco": "https://taittsuu.com/users/reco",
        "https://taittsuu.com/users/mitinoana/profiles": "https://taittsuu.com/users/mitinoana",
    },
    TaittsuuPostUrl: {
        "https://taittsuu.com/users/reco/status/5791570": "https://taittsuu.com/users/reco/status/5791570",
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
        url_string="https://taittsuu.com/users/reco",
        url_type=TaittsuuArtistUrl,
        url_properties=dict(username="reco"),
        primary_names=["れこ"],
        secondary_names=["reco"],
        related=["https://www.pixiv.net/users/1987712"],
    )
