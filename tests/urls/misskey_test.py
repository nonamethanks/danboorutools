import pytest

from danboorutools.logical.urls.misskey import MisskeyAssetUrl, MisskeyNoteUrl, MisskeyUserIdUrl, MisskeyUserUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl, _TestRedirectUrl

urls = {
    MisskeyUserUrl: {
        "https://misskey.io/@snail0326": "https://misskey.io/@snail0326",
    },
    MisskeyUserIdUrl: {
        "https://misskey.io/users/9hlc3rsola": "https://misskey.io/users/9hlc3rsola",
    },
    MisskeyNoteUrl: {
        "https://misskey.io/notes/9rqcaz2nkmbz0esz#pswp": "https://misskey.io/notes/9rqcaz2nkmbz0esz",
    },
    MisskeyAssetUrl: {
        "https://media.misskeyusercontent.jp/io/webpublic-8cebee13-e4f8-4ac4-8c2e-07f0fc26bb7a.webp": "",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestMisskeyUserUrl(_TestArtistUrl):
    url_string = "https://misskey.io/@ChobitsX4"
    url_type = MisskeyUserUrl
    url_properties = dict(username="ChobitsX4")
    primary_names = ["ぶじうさ"]
    secondary_names = ["ChobitsX4"]
    related = ["https://www.patreon.com/ChobitsX4", "http://pixiv.net/users/211326"]


class TestMisskeyUserIdUrl(_TestRedirectUrl):
    url_string = "https://misskey.io/users/9hlc3rsola"
    url_type = MisskeyUserIdUrl
    url_properties = dict(user_id="9hlc3rsola")
    redirects_to = "https://misskey.io/@peach11_01"
