import pytest

from danboorutools.logical.urls.instagram import InstagramArtistUrl, InstagramPostUrl
from tests.helpers.parsing import generate_parsing_test

urls = {
    InstagramArtistUrl: {
        "https://www.instagram.com/itomugi/": "https://www.instagram.com/itomugi",
        "https://www.instagram.com/itomugi/tagged/": "https://www.instagram.com/itomugi",
        "https://www.instagram.com/stories/itomugi/": "https://www.instagram.com/itomugi",
        "https://www.instagram.com/accounts/login/?next=https%3A%2F%2Fwww.instagram.com%2Fed_bkh%2F&is_from_rle": "https://www.instagram.com/ed_bkh"
    },
    InstagramPostUrl: {
        "https://www.instagram.com/p/CbDW9mVuEnn/": "https://www.instagram.com/p/CbDW9mVuEnn",
        "https://www.instagram.com/reel/CV7mHEwgbeF/?utm_medium=copy_link": "https://www.instagram.com/p/CV7mHEwgbeF",
        "https://www.instagram.com/tv/CMjUD1epVWW/": "https://www.instagram.com/p/CMjUD1epVWW",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
