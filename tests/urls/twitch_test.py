from danboorutools.logical.urls.twitch import TwitchChannelUrl, TwitchVideoUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    TwitchChannelUrl: {
        "https://twitch.tv/ayayameko": "https://twitch.tv/ayayameko",
        "https://zh-tw.twitch.tv/sukalee/": "https://twitch.tv/sukalee",
        "https://m.twitch.tv/inkingmetal/home": "https://twitch.tv/inkingmetal",
        "https://twitch.com/inkingmetal": "https://twitch.tv/inkingmetal",
    },
    TwitchVideoUrl: {
        "https://www.twitch.tv/videos/891413875": "https://twitch.tv/videos/891413875",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    url="https://www.twitch.tv/ayayameko",
    url_type=TwitchChannelUrl,
    url_properties=dict(username="ayayameko"),
    primary_names=[],
    secondary_names=["ayayameko"],
    related=[],
)
