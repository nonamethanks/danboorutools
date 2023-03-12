from danboorutools.logical.extractors.line import LineArtistUrl, LineMangaAuthorUrl, LinePostUrl
from tests.extractors import assert_url, generate_parsing_suite

urls = {
    LineArtistUrl: {
        "https://store.line.me/stickershop/author/1140847": "https://store.line.me/stickershop/author/1140847",
        "http://line.me/S/shop/sticker/author/70196": "https://store.line.me/stickershop/author/70196",
    },
    LinePostUrl: {
        "https://store.line.me/stickershop/product/24269/en": "https://store.line.me/stickershop/product/24269",
        "https://store.line.me/stickershop/detail?packageId=1003926": "https://store.line.me/stickershop/product/1003926",
        "http://line.me/S/sticker/1363414": "https://store.line.me/stickershop/product/1363414",
    },
    LineMangaAuthorUrl: {
        "http://manga.line.me/indies/author/detail?author_id=761": "https://manga.line.me/indies/author/detail?author_id=761",
    },
}


generate_parsing_suite(urls)

assert_url(
    "https://store.line.me/stickershop/author/1140847/en",
    url_type=LineArtistUrl,
    url_properties=dict(artist_id=1140847),
    is_deleted=True,
)
