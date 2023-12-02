import pytest

from danboorutools.logical.urls.anifty import AniftyArtistImageUrl, AniftyArtistUrl, AniftyImageUrl, AniftyPostUrl, AniftyTokenUrl
from tests.helpers.parsing import generate_parsing_test

urls = {
    AniftyPostUrl: {
        "https://anifty.jp/creations/373": "https://anifty.jp/creations/373",
        "https://anifty.jp/ja/creations/373": "https://anifty.jp/creations/373",
        "https://anifty.jp/zh/creations/373": "https://anifty.jp/creations/373",
        "https://anifty.jp/zh-Hant/creations/373": "https://anifty.jp/creations/373",
    },
    AniftyArtistUrl: {
        "https://anifty.jp/@hightree": "https://anifty.jp/@hightree",
        "https://anifty.jp/ja/@hightree": "https://anifty.jp/@hightree",
    },
    AniftyTokenUrl: {
        "https://anifty.jp/tokens/17": "https://anifty.jp/tokens/17",
    },
    AniftyImageUrl: {
        "https://anifty.imgix.net/creation/0x961d09077b4a9f7a27f6b7ee78cb4c26f0e72c18/20d5ce5b5163a71258e1d0ee152a0347bf40c7da.png?w=660&h=660&fit=crop&crop=focalpoint&fp-x=0.76&fp-y=0.5&fp-z=1&auto=compress": "",
        "https://anifty.imgix.net/creation/0x961d09077b4a9f7a27f6b7ee78cb4c26f0e72c18/48b1409838cf7271413480b8533372844b9f2437.png?w=3840&q=undefined&auto=compress": "",

        "https://storage.googleapis.com/anifty-media/creation/0x961d09077b4a9f7a27f6b7ee78cb4c26f0e72c18/20d5ce5b5163a71258e1d0ee152a0347bf40c7da.png": "",
    },
    AniftyArtistImageUrl: {
        "https://storage.googleapis.com/anifty-media/profile/0x961d09077b4a9f7a27f6b7ee78cb4c26f0e72c18/a6d2c366a3e876ddbf04fc269b63124be18af424.png": "",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
