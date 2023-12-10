import pytest

from danboorutools.logical.urls.piapro import PiaproArtistUrl, PiaproPostUrl
from danboorutools.logical.urls.tumblr import TumblrArtistUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    PiaproArtistUrl: {
        "http://piapro.jp/ooyuko29": "https://piapro.jp/ooyuko29",
    },
    PiaproPostUrl: {
        "https://piapro.jp/t/Z8xi": "https://piapro.jp/t/Z8xi",
        "http://piapro.jp/content/7vmui67vj0uabnoc": "https://piapro.jp/content/7vmui67vj0uabnoc",
        "https://piapro.jp/t/01ix/20161127225144": "https://piapro.jp/t/01ix",
        "http://piapro.jp/a/content/?id=ncdt0qjsdpdb0lrk": "https://piapro.jp/content/ncdt0qjsdpdb0lrk",
    },
    TumblrArtistUrl: {
        "https://piapro.jp/jump/?url=https%3A%2F%2Fitoiss.tumblr.com": "https://itoiss.tumblr.com",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestPiaproArtistUrl1(_TestArtistUrl):
    url_string = "https://piapro.jp/woki_woki_chi"
    url_type = PiaproArtistUrl
    url_properties = dict(username="woki_woki_chi")
    primary_names = []
    secondary_names = ["woki_woki_chi"]
    related = []
    is_deleted = True


class TestPiaproArtistUrl2(_TestArtistUrl):
    url_string = "https://piapro.jp/saisaiya"
    url_type = PiaproArtistUrl
    url_properties = dict(username="saisaiya")
    primary_names = ["やさい"]
    secondary_names = ["saisaiya"]
    related = ["https://twitter.com/saisaiya"]
