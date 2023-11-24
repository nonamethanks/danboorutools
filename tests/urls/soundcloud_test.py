from danboorutools.logical.urls.soundcloud import SoundcloudArtistRedirectUrl, SoundcloudArtistUrl, SoundcloudPostSetUrl, SoundcloudPostUrl
from tests.urls import assert_artist_url, assert_redirect_url, generate_parsing_suite

urls = {
    SoundcloudArtistUrl: {
        "https://soundcloud.com/k0c3j9j7ct2t": "https://soundcloud.com/k0c3j9j7ct2t",
        "https://www.soundcloud.com/redshiftvocaloid": "https://soundcloud.com/redshiftvocaloid",
        "https://soundcloud.com/user-733647836?p=a&c=1&si=4853ff7929ba4d1e86f42a0f1098b520": "https://soundcloud.com/user-733647836",
        "https://m.soundcloud.com/uchu_c210": "https://soundcloud.com/uchu_c210",
    },
    SoundcloudPostUrl: {
        "https://soundcloud.com/user-70138625/sandrine-price-character-demo-may-2020": "https://soundcloud.com/user-70138625/sandrine-price-character-demo-may-2020",
    },
    SoundcloudPostSetUrl: {
        "https://soundcloud.com/user-279939975/sets/7qi1o5xkayu5": "https://soundcloud.com/user-279939975/sets/7qi1o5xkayu5",
    },
    SoundcloudArtistRedirectUrl: {
        "https://on.soundcloud.com/U6Ah3": "https://on.soundcloud.com/U6Ah3",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    url="https://soundcloud.com/user-798138171",
    url_type=SoundcloudArtistUrl,
    url_properties=dict(username="user-798138171"),
    primary_names=["とりざき"],
    secondary_names=[],
    related=[],
)

assert_redirect_url(
    "https://on.soundcloud.com/U6Ah3",
    url_type=SoundcloudArtistRedirectUrl,
    url_properties=dict(redirect_id="U6Ah3"),
    redirects_to="https://soundcloud.com/saruky",
)
