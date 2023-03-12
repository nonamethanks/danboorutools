from danboorutools.logical.extractors.bcy import BcyArtistUrl, BcyPostUrl
from tests.extractors import generate_parsing_suite

urls = {
    BcyArtistUrl: {
        "https://bcy.net/u/2825982/like": "https://bcy.net/u/2825982",
    },
    BcyPostUrl: {
        "https://bcy.net/item/detail/6576655701886632206?_source_page=": "https://bcy.net/item/detail/6576655701886632206?_source_page=",
    },
    BcyPostUrl: {
        "http://bcy.net/illust/detail/9988/801318": "http://bcy.net/illust/detail/9988/801318",
    },
}


generate_parsing_suite(urls)
