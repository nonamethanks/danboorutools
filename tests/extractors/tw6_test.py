from danboorutools.logical.extractors.tw6 import Tw6ArtistUrl
from tests.extractors import assert_artist_url, generate_parsing_suite

urls = {
    Tw6ArtistUrl: {
        "https://tw6.jp/gallery/master/?master_id=05344": "https://tw6.jp/gallery/master/?master_id=5344",
    },
}


generate_parsing_suite(urls)


assert_artist_url(
    "https://tw6.jp/gallery/master/?master_id=05344",
    url_type=Tw6ArtistUrl,
    url_properties=dict(user_id=5344),
    primary_names=["いもーす"],
    secondary_names=[],
    related=[],
)
