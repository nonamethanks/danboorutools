from danboorutools.logical.urls.togetter import TogetterArtistUrl, TogetterLiUrl, TogetterPostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    TogetterPostUrl: {
        "https://min.togetter.com/yF7scb6": "https://min.togetter.com/yF7scb6",
    },
    TogetterArtistUrl: {
        "https://min.togetter.com/id/srm_chi": "https://min.togetter.com/id/srm_chi",
    },
    TogetterLiUrl: {
        "https://togetter.com/li/107987": "https://togetter.com/li/107987",
    },
}


generate_parsing_suite(urls)


assert_artist_url(
    "https://min.togetter.com/id/srm_chi",
    TogetterArtistUrl,
    url_properties=dict(username="srm_chi"),
    primary_names=[],
    secondary_names=["srm_chi"],
    related=["https://twitter.com/srm_chi"],
    is_deleted=True,
)
