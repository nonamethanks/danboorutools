from danboorutools.logical.urls.fiverr import FiverrArtistUrl, FiverrPostUrl, FiverrShareUrl
from tests.urls import assert_artist_url, assert_redirect_url, generate_parsing_suite

urls = {
    FiverrArtistUrl: {
        "https://www.fiverr.com/eggrollfishh7": "https://www.fiverr.com/eggrollfishh7",
        "https://www.fiverr.com/cindycc07?source=order_page_details_seller_link": "https://www.fiverr.com/cindycc07",
    },
    FiverrPostUrl: {
        "https://www.fiverr.com/eggrollfishh7/draw-you-anime-waifu?utm_campaign=gigs_show&utm_medium=shared&utm_source=copy_link&utm_term=1vrzl6": "https://www.fiverr.com/eggrollfishh7/draw-you-anime-waifu",
    },
    FiverrShareUrl: {
        "https://www.fiverr.com/share/e6XK3Y": "https://www.fiverr.com/share/e6XK3Y",
        "https://www.fiverr.com/s2/3d04bb16ba": "https://www.fiverr.com/s2/3d04bb16ba",
    },
}


generate_parsing_suite(urls)

assert_redirect_url(
    "https://www.fiverr.com/s2/3d04bb16ba",
    url_type=FiverrShareUrl,
    url_properties=dict(subdir="s2", share_code="3d04bb16ba"),
    redirects_to="https://www.fiverr.com/hime_tyan_art/paint-you-a-beautiful-portrait-in-my-style",
)

assert_artist_url(
    "https://www.fiverr.com/eggrollfishh7",
    url_type=FiverrArtistUrl,
    url_properties=dict(artist_name="eggrollfishh7"),
    primary_names=[],
    secondary_names=["eggrollfishh7"],
    related=[],
)
