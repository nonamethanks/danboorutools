import pytest

from danboorutools.logical.urls import line as l
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    l.LineArtistUrl: {
        "https://store.line.me/stickershop/author/1140847": "https://store.line.me/stickershop/author/1140847",
        "http://line.me/S/shop/sticker/author/70196": "https://store.line.me/stickershop/author/70196",
        "https://store.line.me/themeshop/author/96136": "https://store.line.me/themeshop/author/96136",
    },
    l.LinePostUrl: {
        "https://store.line.me/stickershop/product/24269/en": "https://store.line.me/stickershop/product/24269",
        "https://store.line.me/stickershop/detail?packageId=1003926": "https://store.line.me/stickershop/product/1003926",
        "http://line.me/S/sticker/1363414": "https://store.line.me/stickershop/product/1363414",
        "https://store.line.me/themeshop/product/37efc43b-ae8e-42ea-b01e-962843180295/en": "https://store.line.me/themeshop/product/37efc43b-ae8e-42ea-b01e-962843180295",
    },
    l.LineMangaAuthorUrl: {
        "http://manga.line.me/indies/author/detail?author_id=761": "https://manga.line.me/indies/author/detail?author_id=761",
    },
    l.LineMusicArtistUrl: {
        "https://music.line.me/webapp/artist/mi000000000000000": "https://music.line.me/webapp/artist/mi000000000000000",
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
        url_string="https://store.line.me/stickershop/author/1140847/en",
        url_type=l.LineArtistUrl,
        url_properties=dict(artist_id=1140847),
        primary_names=[],
        secondary_names=[],
        related=[],
        is_deleted=True,
    )
