from danboorutools.logical.urls.throne import ThroneArtistUrl, ThronePostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    ThroneArtistUrl: {
        "https://throne.com/rins/wishlist": "https://throne.com/rins",
        "https://throne.com/rins": "https://throne.com/rins",
        "https://jointhrone.com/u/brittanybabbles": "https://throne.com/brittanybabbles",
    },
    ThronePostUrl: {
        "https://throne.com/brittanybabbles/item/aee67ff0-c78c-4ffa-879a-40d9f6eee670": "https://throne.com/brittanybabbles/item/aee67ff0-c78c-4ffa-879a-40d9f6eee670",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    url="https://throne.com/iomaaki",
    url_type=ThroneArtistUrl,
    url_properties=dict(username="iomaaki"),
    primary_names=["mae"],
    secondary_names=["iomaaki"],
    related=["https://twitter.com/iomaaki", "https://twitch.tv/iomaaki", "https://iomaaki.carrd.co/"],
)
