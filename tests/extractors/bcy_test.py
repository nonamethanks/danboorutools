from danboorutools.logical.extractors.bcy import BcyArtistUrl, BcyPostUrl, OldBcyPostUrl
from tests.extractors import assert_artist_url, generate_parsing_suite

urls = {
    BcyArtistUrl: {
        "https://bcy.net/u/2825982/like": "https://bcy.net/u/2825982",
    },
    BcyPostUrl: {
        "https://bcy.net/item/detail/6576655701886632206?_source_page=": "https://bcy.net/item/detail/6576655701886632206",
    },
    OldBcyPostUrl: {
        "http://bcy.net/illust/detail/9988/801318": "https://bcy.net/illust/detail/9988/801318",
        "https://bcy.net/illust/detail/158436": "https://bcy.net/illust/detail/158436",
        "https://bcy.net/coser/detail/89784": "https://bcy.net/illust/detail/89784",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    "https://bcy.net/u/2825982",
    url_type=BcyArtistUrl,
    url_properties=dict(user_id=2825982),
    primary_names=["Leo_Thasario"],
    secondary_names=[],
    related=[],
)
