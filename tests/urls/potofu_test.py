import pytest

from danboorutools.logical.urls.potofu import PotofuArtistUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestInfoUrl

urls = {
    PotofuArtistUrl: {
        "https://potofu.me/158161163": "https://potofu.me/158161163",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestPotofuArtistUrl(_TestInfoUrl):
    url_string = "https://potofu.me/158161163"
    url_type = PotofuArtistUrl
    url_properties = dict(user_id="158161163")
    related = [
        "https://marshmallow-qa.com/_158161163",
        "https://mobile.twitter.com/_158161163",
        "https://pawoo.net/@_158161163",
        "https://skeb.jp/@_158161163",
        "https://www.pixiv.net/en/users/88293257",
    ]
    primary_names = ["錫i", "suzzu"]
    secondary_names = []
