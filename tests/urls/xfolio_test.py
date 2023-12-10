import pytest

from danboorutools.logical.urls.xfolio import XfolioArtistUrl, XfolioPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    XfolioArtistUrl: {
        "https://xfolio.jp/portfolio/hayato69": "https://xfolio.jp/portfolio/hayato69",
        "https://xfolio.jp/portfolio/hayato69/free/33407": "https://xfolio.jp/portfolio/hayato69",
        "https://xfolio.jp/portfolio/hayato69/works": "https://xfolio.jp/portfolio/hayato69",
    },
    XfolioPostUrl: {
        "https://xfolio.jp/portfolio/Rei_0127/works/59931": "https://xfolio.jp/portfolio/Rei_0127/works/59931",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestXfolioArtistUrl1(_TestArtistUrl):
    url_string = "https://xfolio.jp/portfolio/hayato69"
    url_type = XfolioArtistUrl
    url_properties = dict(username="hayato69")
    primary_names = ["隼人ろっく"]
    secondary_names = ["hayato69"]
    related = [
        "https://www.pixiv.net/en/users/374228",
        "https://marshmallow-qa.com/25qvu24jj41loap",
        "https://www.youtube.com/channel/UCtKqZDgqH9QnxJYeF0GDReQ",
        "https://www.youtube.com/playlist?list=PLcw27-K4pcr1dpfhogJcBGhsqqkSWbu4K",
        "https://www.youtube.com/playlist?list=PLcw27-K4pcr1mBTP96oqZACZlNd-1xS5M",
        "https://www.youtube.com/playlist?list=PLcw27-K4pcr23t305PlCpIYvulr0m2Agu",
    ]


class TestXfolioArtistUrl2(_TestArtistUrl):
    url_string = "https://xfolio.jp/portfolio/negi_toro07"
    url_type = XfolioArtistUrl
    url_properties = dict(username="negi_toro07")
    primary_names = ["ねぎとろ"]
    secondary_names = ["negi_toro07"]
    related = [
        "https://twitter.com/negi_toro07",
        "https://www.instagram.com/negi_toro07/",
        "https://coconala.com/mypage/user",
        "https://skeb.jp/@negi_toro07",
        "https://skima.jp/profile?id=276250",
        "https://www.pixiv.net/users/14253416",
    ]
