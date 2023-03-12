from danboorutools.logical.extractors.line import LineArtistUrl, LinePostUrl
from tests.extractors import assert_url, generate_parsing_suite

urls = {
    LineArtistUrl: {
        "https://store.line.me/stickershop/author/1140847": "https://store.line.me/stickershop/author/1140847",
    },
    LinePostUrl: {
        "https://store.line.me/stickershop/product/24269/en": "https://store.line.me/stickershop/product/24269",
    },
}


generate_parsing_suite(urls)

assert_url(
    "https://store.line.me/stickershop/author/1140847/en",
    url_type=LineArtistUrl,
    url_properties=dict(artist_id=1140847),
    is_deleted=True,
)
