import pytest

from danboorutools.logical.urls.threads import ThreadsArtistUrl, ThreadsPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    ThreadsArtistUrl: {
        "https://www.threads.net/@mawari5577": "https://www.threads.net/@mawari5577",
    },
    ThreadsPostUrl: {
        "https://www.threads.net/@saikou.jp/post/CvX2h-wJCTe.jpg": "https://www.threads.net/@saikou.jp/post/CvX2h-wJCTe",
        "https://www.threads.net/@saikou.jp/post/Cvabd9_PAbI": "https://www.threads.net/@saikou.jp/post/Cvabd9_PAbI",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_artist_url_1():
    generate_artist_test(
        url_string="https://www.threads.net/@mawari5577",
        url_type=ThreadsArtistUrl,
        url_properties=dict(username="mawari5577"),
        primary_names=["海猫まわり"],
        secondary_names=["mawari5577"],
        related=["https://www.instagram.com/mawari5577/"],
    )
