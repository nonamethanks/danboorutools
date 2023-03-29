from danboorutools.logical.urls.skima import SkimaArtistUrl, SkimaGalleryUrl, SkimaImageUrl, SkimaItemUrl
from danboorutools.logical.urls.stash import StaShUrl
from tests.urls import generate_parsing_suite

urls = {
    StaShUrl: {
        "https://sta.sh/21leo8mz87ue": "https://sta.sh/21leo8mz87ue",
        "https://sta.sh/2uk0v5wabdt": "https://sta.sh/2uk0v5wabdt",
        "https://sta.sh/0wxs31o7nn2": "https://sta.sh/0wxs31o7nn2",
    },
}

generate_parsing_suite(urls)
