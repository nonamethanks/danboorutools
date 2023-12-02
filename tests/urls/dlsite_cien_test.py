import pytest

from danboorutools.logical.urls.dlsite_cien import DlsiteCienArticleUrl, DlsiteCienCreatorUrl, DlsiteCienProfileUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_info_test

urls = {
    DlsiteCienCreatorUrl: {
        "https://ci-en.dlsite.com/creator/3894": "https://ci-en.dlsite.com/creator/3894",
        "https://ci-en.dlsite.com/creator/12346/shop": "https://ci-en.dlsite.com/creator/12346",
    },
    DlsiteCienArticleUrl: {
        "https://ci-en.dlsite.com/creator/3894/article/684012": "https://ci-en.dlsite.com/creator/3894/article/684012",
    },
    DlsiteCienProfileUrl: {
        "https://ci-en.dlsite.com/profile/746780": "https://ci-en.dlsite.com/profile/746780",
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
        url_string="https://ci-en.dlsite.com/creator/16182",
        url_type=DlsiteCienCreatorUrl,
        url_properties=dict(creator_id=16182),
        primary_names=["ナナバラメイ"],
        secondary_names=[],
        related=[
            "https://skeb.jp/@7rose_may",
            "https://twitter.com/7rose_may2",
            "https://www.pixiv.net/en/users/11823554",
        ],
    )
