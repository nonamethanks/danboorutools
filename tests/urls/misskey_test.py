from danboorutools.logical.urls.misskey import MisskeyUserUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    MisskeyUserUrl: {
        "https://misskey.io/@snail0326": "https://misskey.io/@snail0326",
    },
}

generate_parsing_suite(urls)


assert_artist_url(
    "https://misskey.io/@ChobitsX4",
    url_type=MisskeyUserUrl,
    url_properties=dict(username="ChobitsX4"),
    primary_names=["ぶじうさ"],
    secondary_names=["ChobitsX4"],
    related=["https://www.patreon.com/ChobitsX4", "http://pixiv.net/users/211326"],
)
