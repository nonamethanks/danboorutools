import pytest

from danboorutools.logical.urls.pixiv_comic import PixivComicStoryUrl, PixivComicWorkUrl
from tests.helpers.parsing import generate_parsing_test

urls = {
    PixivComicStoryUrl: {
        "https://comic.pixiv.net/viewer/stories/107927": "https://comic.pixiv.net/viewer/stories/107927",
    },
    PixivComicWorkUrl: {
        "https://comic.pixiv.net/works/8683": "https://comic.pixiv.net/works/8683",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
