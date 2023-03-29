from danboorutools.logical.urls.dlsite_cien import DlsiteCienArticleUrl, DlsiteCienCreatorUrl, DlsiteCienProfileUrl
from tests.urls import assert_info_url, generate_parsing_suite

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


generate_parsing_suite(urls)


assert_info_url(
    "https://ci-en.dlsite.com/creator/16182",
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
