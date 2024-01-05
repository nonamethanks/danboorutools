import pytest

from danboorutools.logical.urls.sblo import SbloArticleUrl, SbloBlogUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    SbloBlogUrl: {
        "http://2go.sblo.jp/": "http://2go.sblo.jp/",
        "http://yuzu-soft.sblo.jp/category/583783-1.html": "http://yuzu-soft.sblo.jp/",
        "http://morionohana.sblo.jp/s/": "http://morionohana.sblo.jp/",
    },
    SbloArticleUrl: {
        "http://inside-otome.sblo.jp/article/41463667.html": "http://inside-otome.sblo.jp/article/41463667.html",
        "http://makkou.sblo.jp/s/article/186701561.html": "http://makkou.sblo.jp/article/186701561.html",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestSbloArtistUrl1(_TestArtistUrl):
    url_string = "http://2go.sblo.jp/"
    url_type = SbloBlogUrl
    url_properties = dict(blog_name="2go")
    primary_names = []
    secondary_names = ["2go"]
    related = []
    is_deleted = True
