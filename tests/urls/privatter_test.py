from danboorutools.logical.urls.privatter import PrivatterArtistUrl, PrivatterImageUrl, PrivatterPostUrl
from tests.urls import assert_artist_url, assert_post_url, generate_parsing_suite

urls = {
    PrivatterPostUrl: {
        "http://privatter.net/p/8096124": "http://privatter.net/p/8096124",
        "http://privatter.net/i/2655076": "http://privatter.net/i/2655076",
    },
    PrivatterArtistUrl: {
        "https://privatter.net/u/uzura_55": "https://privatter.net/u/uzura_55",
        "https://privatter.net/m/naoaraaa04": "https://privatter.net/u/naoaraaa04",
    },
    PrivatterImageUrl: {
        "http://privatter.net/img_original/856121876520129d361c6e.jpg": "http://privatter.net/img_original/856121876520129d361c6e.jpg",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    "https://privatter.net/u/uzura_55",
    url_type=PrivatterArtistUrl,
    url_properties=dict(username="uzura_55"),
    primary_names=[],
    secondary_names=["uzura_55"],
    related=["https://www.twitter.com/uzura_55"],
)


assert_post_url(
    "http://privatter.net/p/8096124",
    url_type=PrivatterPostUrl,
    url_properties=dict(post_id=8096124, post_type="p"),
    gallery="",
)
