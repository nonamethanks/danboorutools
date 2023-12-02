import pytest

from danboorutools.logical.urls.kakuyomu import KakuyomuArtistUrl, KakuyomuPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test, generate_post_test

urls = {
    KakuyomuArtistUrl: {
        "http://kakuyomu.jp/users/warugi871": "https://kakuyomu.jp/users/warugi871",
    },
    KakuyomuPostUrl: {
        "https://kakuyomu.jp/works/4852201425154874772": "https://kakuyomu.jp/works/4852201425154874772",
        "https://kakuyomu.jp/my/works/16816927860914502743": "https://kakuyomu.jp/works/16816927860914502743",
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
        url_string="http://kakuyomu.jp/users/warugi871",
        url_type=KakuyomuArtistUrl,
        url_properties=dict(username="warugi871"),
        primary_names=["羽流木はない"],
        secondary_names=["warugi871"],
        related=["https://twitter.com/warugi871"],
    )


def test_post_url_1():
    generate_post_test(
        url_string="https://kakuyomu.jp/works/16817330659778429227",
        url_type=KakuyomuPostUrl,
        url_properties=dict(post_id=16817330659778429227),
        gallery="https://kakuyomu.jp/users/parantica_sita",
    )
