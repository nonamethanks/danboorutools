import pytest

from danboorutools.logical.urls.clipstudio import (
    ClipStudioAssetPostUrl,
    ClipStudioBlogUrl,
    ClipStudioProfileUrl,
    ClipStudioUserSearchUrl,
)
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestInfoUrl

urls = {
    ClipStudioAssetPostUrl: {
        "https://assets.clip-studio.com/ja-jp/detail?id=1946309": "https://assets.clip-studio.com/en-us/detail?id=1946309",
    },
    ClipStudioProfileUrl: {
        "https://profile.clip-studio.com/ja-jp/profile/cxhgegm-sc": "https://profile.clip-studio.com/en-us/profile/cxhgegm-sc",
        "https://profile.clip-studio.com/en-us/profile/gch9jit-cw": "https://profile.clip-studio.com/en-us/profile/gch9jit-cw",
    },
    ClipStudioUserSearchUrl: {
        "https://assets.clip-studio.com/ja-jp/search?user=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8F&order=new": "https://assets.clip-studio.com/en-us/search?user=隼人ろっく",
    },
    ClipStudioBlogUrl: {
        "http://fuujin.sees.clip-studio.com/": "http://fuujin.sees.clip-studio.com/site/",
        "http://fuujin.sees.clip-studio.com/site/": "http://fuujin.sees.clip-studio.com/site/",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestClipStudioBlogUrl(_TestInfoUrl):
    url_string = "http://fuujin.sees.clip-studio.com"
    url_type = ClipStudioBlogUrl
    url_properties = dict(blog_name="fuujin")
    primary_names = []
    secondary_names = ["fuujin"]
    related = []
    is_deleted = True
