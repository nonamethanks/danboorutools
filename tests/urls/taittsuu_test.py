from danboorutools.logical.urls.taittsuu import TaittsuuArtistUrl, TaittsuuPostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    TaittsuuArtistUrl: {
        "https://taittsuu.com/users/reco": "https://taittsuu.com/users/reco",
        "https://taittsuu.com/users/mitinoana/profiles": "https://taittsuu.com/users/mitinoana",
    },
    TaittsuuPostUrl: {
        "https://taittsuu.com/users/reco/status/5791570": "https://taittsuu.com/users/reco/status/5791570",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    url="https://taittsuu.com/users/reco",
    url_type=TaittsuuArtistUrl,
    url_properties=dict(username="reco"),
    primary_names=["れこ"],
    secondary_names=["reco"],
    related=["https://www.pixiv.net/users/1987712"],
)
