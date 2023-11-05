from danboorutools.logical.urls.crepu import CrepuArtistUrl, CrepuPostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    CrepuArtistUrl: {
        "https://crepu.net/user/shio_332": "https://crepu.net/user/shio_332",
    },
    CrepuPostUrl: {
        "https://crepu.net/post/264943":"https://crepu.net/post/264943",
    },
}


generate_parsing_suite(urls)


assert_artist_url(
    url="https://crepu.net/user/shio_332",
    url_type=CrepuArtistUrl,
    url_properties=dict(username="shio_332"),
    primary_names=["汐見"],
    secondary_names=["shio_332"],
    related=["https://twitter.com/nomiya332", "https://www.pixiv.net/users/87958749", "https://xfolio.jp/portfolio/nomiya332"],
)
