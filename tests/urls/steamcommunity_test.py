import pytest

from danboorutools.logical.urls.steamcommunity import SteamcommunityFileUrl, SteamCommunityProfileUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    SteamCommunityProfileUrl: {
        "https://steamcommunity.com/id/dicenaries-tech/myworkshopfiles": "https://steamcommunity.com/id/dicenaries-tech",
        "http://steamcommunity.com/profiles/76561198121582231/myworkshopfiles": "https://steamcommunity.com/profiles/76561198121582231",
    },
    SteamcommunityFileUrl: {
        "http://steamcommunity.com/sharedfiles/filedetails/?id=663874840&amp;tscn=1467002725": "https://steamcommunity.com/sharedfiles/filedetails/?id=663874840",
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
        url_string="https://steamcommunity.com/id/dicenaries-tech",
        url_type=SteamCommunityProfileUrl,
        url_properties=dict(username="dicenaries-tech"),
        primary_names=["Dinnyforst"],
        secondary_names=["dicenaries-tech"],
        related=[
            "https://twitter.com/Dinnyforst",
            "https://pixiv.me/dinnyforst",
            "https://www.artstation.com/dinnyforst",
            "https://www.deviantart.com/dinnyforst",
            "https://www.facebook.com/DinnyforstArt/",
            "https://drive.google.com/file/d/0B-LlruTRou9AZUFpX2tFVE1fOVE/view",
            "https://drive.google.com/file/d/16gT8Y4ernqrIpjoDX7QvR57lQBLxjIUD/view",
            "https://drive.google.com/file/d/1kEj-qCh88_G4vNBQ6Njv5iZh9d_ixNzp/view",
            "https://drive.google.com/file/d/1tOsnzGu4YFsLk6RbCAN0I-Fn2umWpVqo/view",
            "https://www.facebook.com/VindictusTh",
            "https://www.facebook.com/media/set/?set=a.1756893337695795.1073741857.100001254376113",
        ],
    )
