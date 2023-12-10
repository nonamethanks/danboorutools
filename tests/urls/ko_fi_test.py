import pytest

from danboorutools.logical.urls.ko_fi import KoFiArtistUrl, KoFiImageUrl, KoFiPostUrl, KofiShopPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

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


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestKoFiArtistUrl1(_TestArtistUrl):
    url_string = "https://ko-fi.com/ririko_riri"
    url_type = KoFiArtistUrl
    url_properties = dict(username="ririko_riri")
    related = []
    primary_names = []
    secondary_names = ["ririko_riri"]
    is_deleted = True


class TestKoFiArtistUrl2(_TestArtistUrl):
    url_string = "https://ko-fi.com/simzart"
    url_type = KoFiArtistUrl
    url_properties = dict(username="simzart")
    related = ["https://go.twitch.tv/simzart/",
               "https://www.instagram.com/simz.art/",
               "https://www.facebook.com/simoneferrieroart",
               "https://twitter.com/SimzArts",
               "https://www.youtube.com/channel/UCc9-wPmgwCAoNJF6a5iC1gQ",
               "https://www.tumblr.com/simzart",
               "https://www.reddit.com/user/simz88",
               "https://www.twitch.tv/SimzArt",
               "https://www.tiktok.com/@simz.art"]
    primary_names = ["Simz"]
    secondary_names = ["simzart"]
