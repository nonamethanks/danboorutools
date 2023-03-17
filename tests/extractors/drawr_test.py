from danboorutools.logical.extractors import newgrounds as ns
from danboorutools.logical.extractors.drawr import DrawrArtistUrl, DrawrImageUrl, DrawrPostUrl
from tests.extractors import generate_parsing_suite

urls = {
    DrawrArtistUrl: {
        "http://drawr.net/ryu_ka29": "https://drawr.net/ryu_ka29",
    },
    DrawrPostUrl: {
        "https://drawr.net/show.php?id=7134935": "https://drawr.net/show.php?id=7134935",
        "http://drawr.net/show.php?id=626397#rid1218652": "https://drawr.net/show.php?id=626397",
    },
    DrawrImageUrl: {
        "http://img05.drawr.net/draw/img/121487/526b6decJWNv2Aaf.png": "http://img05.drawr.net/draw/img/121487/526b6decJWNv2Aaf.png",
    },
}

generate_parsing_suite(urls)
