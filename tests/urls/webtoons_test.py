import pytest

from danboorutools.logical.urls.webtoons import WebtoonsArtistNoLanguageUrl, WebtoonsArtistUrl, WebtoonsChapterUrl, WebtoonsWebtoonUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl, _TestRedirectUrl

urls = {
    WebtoonsWebtoonUrl: {
        "https://www.webtoons.com/en/challenge/starlight/list?title_no=352771": "https://www.webtoons.com/en/challenge/starlight/list?title_no=352771",
        "https://www.webtoons.com/fr/challenge/pix-paradise-in-xelio/synopsis/viewer?title_no=723424": "https://www.webtoons.com/fr/challenge/pix-paradise-in-xelio/list?title_no=723424",
    },
    WebtoonsChapterUrl: {
        "https://www.webtoons.com/en/challenge/faded-away/prologue/viewer?title_no=214314&episode_no=1": "https://www.webtoons.com/en/challenge/faded-away/prologue/viewer?title_no=214314&episode_no=1",
    },
    WebtoonsArtistUrl: {
        "https://www.webtoons.com/en/creator/37u4n": "https://www.webtoons.com/en/creator/37u4n",
    },
    WebtoonsArtistNoLanguageUrl: {
        "https://www.webtoons.com/creator/h25s6": "https://www.webtoons.com/creator/h25s6",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestWebtoonsArtistUrl(_TestArtistUrl):
    url_string = "https://www.webtoons.com/id/creator/h25s6"
    url_type = WebtoonsArtistUrl
    url_properties = dict(creator_id="h25s6", language="id")
    primary_names = ["Leaf19"]
    secondary_names = []
    related = []


class TestWebtoonsArtistNoLanguageUrl(_TestRedirectUrl):
    url_string = "https://www.webtoons.com/creator/h25s6"
    url_type = WebtoonsArtistNoLanguageUrl
    url_properties = dict(creator_id="h25s6")
    redirects_to = "https://www.webtoons.com/id/creator/h25s6"
