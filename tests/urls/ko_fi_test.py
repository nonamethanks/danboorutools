from danboorutools.logical.urls.ko_fi import KoFiArtistUrl, KoFiImageUrl, KoFiPostUrl, KofiShopPostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    KoFiArtistUrl: {
        "https://ko-fi.com/homuchisas/commissions#buyCommissionModal": "https://ko-fi.com/homuchisas",
        "https://ko-fi.com/chrisplus/gallery": "https://ko-fi.com/chrisplus",
        "https://ko-fi.com/chezforshire/commissions": "https://ko-fi.com/chezforshire",
    },
    KoFiPostUrl: {
        "https://ko-fi.com/i/IW7W1JB2Y2": "https://ko-fi.com/i/IW7W1JB2Y2",
        "https://ko-fi.com/annluvazzel?viewimage=IE1E1FSB3S#galleryItemView": "https://ko-fi.com/i/IE1E1FSB3S",
    },
    KoFiImageUrl: {
        "https://storage.ko-fi.com/cdn/useruploads/post/85da18f0-3fe5-4523-a67c-a6e787e3c2b2_evesnow.jpg": "https://storage.ko-fi.com/cdn/useruploads/display/85da18f0-3fe5-4523-a67c-a6e787e3c2b2_evesnow.jpg",
        "https://storage.ko-fi.com/cdn/useruploads/display/85da18f0-3fe5-4523-a67c-a6e787e3c2b2_evesnow.jpg": "https://storage.ko-fi.com/cdn/useruploads/display/85da18f0-3fe5-4523-a67c-a6e787e3c2b2_evesnow.jpg",  # sample
        "https://cdn.ko-fi.com/cdn/useruploads/png_ff346213-aa20-40da-a0b3-f9d7d7c3e714sharable.png?v=c15575cb-7144-4019-9f44-5be7a5cf2ad8": "https://cdn.ko-fi.com/cdn/useruploads/png_ff346213-aa20-40da-a0b3-f9d7d7c3e714sharable.png",
    },
    KofiShopPostUrl: {
        "https://ko-fi.com/s/587d9729ac": "https://ko-fi.com/s/587d9729ac",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    url="https://ko-fi.com/ririko_riri",
    url_type=KoFiArtistUrl,
    url_properties=dict(username="ririko_riri"),
    related=["https://ririkos-commissions.carrd.co/", "https://twitter.com/Ririko_Ri_Ri", "https://www.twitch.tv/Ririko_Riri"],
    primary_names=["Riri 🌧️"],
    secondary_names=["ririko_riri"],
)
