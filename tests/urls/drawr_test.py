import pytest

from danboorutools.logical.urls.drawr import DrawrArtistUrl, DrawrImageUrl, DrawrPostUrl
from tests.helpers.parsing import generate_parsing_test

urls = {
    DrawrArtistUrl: {
        "http://drawr.net/ryu_ka29": "https://drawr.net/ryu_ka29",
    },
    DrawrPostUrl: {
        "https://drawr.net/show.php?id=7134935": "https://drawr.net/show.php?id=7134935",
        "http://drawr.net/show.php?id=626397#rid1218652": "https://drawr.net/show.php?id=626397",
    },
    DrawrImageUrl: {
        "http://img05.drawr.net/draw/img/121487/526b6decJWNv2Aaf.png": "http://img05.drawr.net/draw/img/121487/526b6decJWNv2Aaf.png",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
