import pytest

from danboorutools.logical.urls.myportfolio import MyportfolioArtistUrl, MyportfolioImageUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    MyportfolioArtistUrl: {
        "https://ramonn90.myportfolio.com": "https://ramonn90.myportfolio.com",
        "https://superfresh20xx.myportfolio.com/profile": "https://superfresh20xx.myportfolio.com",
    },
    MyportfolioImageUrl: {
        "https://cdn.myportfolio.com/3a87c4599bde55ea6e62b2756c9e48ab/42f58234-c715-47f4-bd48-27e544821696_rw_1200.jpg?h=c36c751fdab41b1c20a5281611ded8dd": "",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestMyportfolioArtistUrl1(_TestArtistUrl):
    url_string = "https://ramonn90.myportfolio.com"
    url_type = MyportfolioArtistUrl
    url_properties = dict(username="ramonn90")
    primary_names = []
    secondary_names = ["ramonn90"]
    related = []


class TestMyportfolioArtistUrl2(_TestArtistUrl):
    url_string = "https://yuk1a01.myportfolio.com"
    url_type = MyportfolioArtistUrl
    url_properties = dict(username="yuk1a01")
    primary_names = []
    secondary_names = ["yuk1a01"]
    related = []
    is_deleted = True
