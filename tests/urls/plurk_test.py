import pytest

from danboorutools.logical.urls.plurk import PlurkArtistUrl, PlurkImageUrl, PlurkPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    PlurkArtistUrl: {
        "https://www.plurk.com/m/redeyehare": "https://www.plurk.com/redeyehare",
        "https://www.plurk.com/u/ddks2923": "https://www.plurk.com/ddks2923",
        "https://www.plurk.com/m/u/leiy1225": "https://www.plurk.com/leiy1225",
        "https://www.plurk.com/s/u/salmonroe13": "https://www.plurk.com/salmonroe13",
        "https://www.plurk.com/redeyehare": "https://www.plurk.com/redeyehare",
        "https://www.plurk.com/RSSSww/invite/4": "https://www.plurk.com/RSSSww",
    },
    PlurkImageUrl: {
        "https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg": "https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg",
        "https://images.plurk.com/mx_5wj6WD0r6y4rLN0DL3sqag.jpg": "https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg",

    },
    PlurkPostUrl: {
        "https://www.plurk.com/p/om6zv4": "https://www.plurk.com/p/om6zv4",
        "https://www.plurk.com/m/p/okxzae": "https://www.plurk.com/p/okxzae",
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
        url_string="https://www.plurk.com/vivi890812",
        url_type=PlurkArtistUrl,
        url_properties=dict(username="vivi890812"),
        primary_names=["犬勇者-CWT65次日 O28"],
        secondary_names=["vivi890812"],
        related=["https://her178542.pixnet.net",
                 "https://home.gamer.com.tw/homeindex.php?owner=her682913",
                 "https://www.pixiv.net/en/users/5253106"],
    )
