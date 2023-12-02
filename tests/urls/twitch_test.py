import pytest

from danboorutools.logical.urls.twitch import TwitchChannelUrl, TwitchVideoUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

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


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_artist_url_1():
    generate_artist_test(
        url_string="https://www.twitch.tv/ayayameko",
        url_type=TwitchChannelUrl,
        url_properties=dict(username="ayayameko"),
        primary_names=[],
        secondary_names=["ayayameko"],
        related=[],
    )
