import pytest

from danboorutools.logical.urls.throne import ThroneArtistUrl, ThronePostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    ThroneArtistUrl: {
        "https://throne.com/rins/wishlist": "https://throne.com/rins",
        "https://throne.com/rins": "https://throne.com/rins",
        "https://jointhrone.com/u/brittanybabbles": "https://throne.com/brittanybabbles",
    },
    ThronePostUrl: {
        "https://throne.com/brittanybabbles/item/aee67ff0-c78c-4ffa-879a-40d9f6eee670": "https://throne.com/brittanybabbles/item/aee67ff0-c78c-4ffa-879a-40d9f6eee670",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestThroneArtistUrl(_TestArtistUrl):
    url_string = "https://throne.com/iomaaki"
    url_type = ThroneArtistUrl
    url_properties = dict(username="iomaaki")
    primary_names = ["mae"]
    secondary_names = ["iomaaki"]
    related = ["https://twitter.com/iomaaki", "https://twitch.tv/iomaaki", "https://iomaaki.carrd.co/"]
