import pytest

from danboorutools.logical.urls.litlink import LitlinkUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_info_test

urls = {
    LitlinkUrl: {
        "https://lit.link/en/hayato69link": "https://lit.link/hayato69link",
        "https://lit.link/mawariartwork": "https://lit.link/mawariartwork",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_info_url_1():
    generate_info_test(
        url_string="https://lit.link/en/hayato69link",
        url_type=LitlinkUrl,
        url_properties=dict(username="hayato69link"),
        primary_names=["隼人ろっく"],
        secondary_names=["hayato69link"],
        related=[
            "https://assets.clip-studio.com/ja-jp/search?user=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8F&order=new",
            "https://bit.ly/3xcRBib",
            "https://skeb.jp/@hayato69rock",
            "https://skima.jp/profile?id=244678",
            "https://store.line.me/stickershop/author/1140847",
            "https://twitter.com/hashtag/ガチャドロック?src=hashtag_click&f=live",
            "https://twitter.com/hayARTo_Rock",
            "https://twitter.com/hayato_Rock_YT",
            "https://www.amazon.jp/hz/wishlist/ls/1O5XMOZHKWBE8?ref_=wl_share",
            "https://www.pixiv.net/users/374228",
            "https://www.youtube.com/channel/UCtKqZDgqH9QnxJYeF0GDReQ",
            "https://www.youtube.com/channel/UCtKqZDgqH9QnxJYeF0GDReQ",
            "https://www.youtube.com/results?search_query=隼人ろっくch&sp=EgIIBA==",
            "https://xfolio.jp/portfolio/hayato69",
            "https://xfolio.jp/portfolio/hayato69/free/33407",
            "https://xfolio.jp/portfolio/hayato69/free/39674",
            "https://youtube.com/playlist?list=PLcw27-K4pcr23t305PlCpIYvulr0m2Agu",
        ],
    )


def test_info_url_2():
    generate_info_test(
        url_string="https://lit.link/en/mawariartwork",
        url_type=LitlinkUrl,
        url_properties=dict(username="mawariartwork"),
        primary_names=[],
        secondary_names=["mawariartwork"],
        related=[],
        is_deleted=True,
    )
