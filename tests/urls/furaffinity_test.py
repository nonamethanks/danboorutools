import pytest

from danboorutools.logical.urls.furaffinity import FuraffinityArtistImageUrl, FuraffinityArtistUrl, FuraffinityImageUrl, FuraffinityPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    FuraffinityArtistUrl: {
        "https://www.furaffinity.net/gallery/iwbitu": "https://www.furaffinity.net/user/iwbitu",
        "https://www.furaffinity.net/scraps/iwbitu/2/?": "https://www.furaffinity.net/user/iwbitu",
        "https://www.furaffinity.net/gallery/iwbitu/folder/133763/Regular-commissions": "https://www.furaffinity.net/user/iwbitu",
        "https://www.furaffinity.net/user/lottieloveart/user?user_id=1021820442510802945": "https://www.furaffinity.net/user/lottieloveart",
        "https://www.furaffinity.net/stats/duskmoor/submissions/": "https://www.furaffinity.net/user/duskmoor",
    },
    FuraffinityImageUrl: {
        "https://d.furaffinity.net/art/iwbitu/1650222955/1650222955.iwbitu_yubi.jpg": "https://d.furaffinity.net/art/iwbitu/1650222955/1650222955.iwbitu_yubi.jpg",
        "https://t.furaffinity.net/46821705@800-1650222955.jpg": "",

    },
    FuraffinityArtistImageUrl: {
        "https://a.furaffinity.net/1550854991/iwbitu.gif": "https://a.furaffinity.net/1550854991/iwbitu.gif",
    },
    FuraffinityPostUrl: {
        "https://www.furaffinity.net/view/46821705/": "https://www.furaffinity.net/view/46821705",
        "https://www.furaffinity.net/view/46802202/": "https://www.furaffinity.net/view/46802202",
        "https://www.furaffinity.net/full/46821705/": "https://www.furaffinity.net/view/46821705",
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
        url_string="https://www.furaffinity.net/user/bb00",
        url_type=FuraffinityArtistUrl,
        url_properties=dict(username="bb00"),
        related=["https://twitter.com/BB00_Art"],
        primary_names=[],
        secondary_names=["bb00"],
    )
