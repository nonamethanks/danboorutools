from danboorutools.logical.extractors.dlsite_cien import DlsiteCienArticleUrl, DlsiteCienCreatorUrl, DlsiteCienProfileUrl
from tests.extractors import generate_parsing_suite

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
    }
}


generate_parsing_suite(urls)
