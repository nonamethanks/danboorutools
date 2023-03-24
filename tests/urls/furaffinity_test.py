from danboorutools.logical.urls.furaffinity import FuraffinityArtistImageUrl, FuraffinityArtistUrl, FuraffinityImageUrl, FuraffinityPostUrl
from tests.urls import generate_parsing_suite

urls = {
    FuraffinityArtistUrl: {
        "https://www.furaffinity.net/gallery/iwbitu": "https://www.furaffinity.net/user/iwbitu",
        "https://www.furaffinity.net/scraps/iwbitu/2/?": "https://www.furaffinity.net/user/iwbitu",
        "https://www.furaffinity.net/gallery/iwbitu/folder/133763/Regular-commissions": "https://www.furaffinity.net/user/iwbitu",
        "https://www.furaffinity.net/user/lottieloveart/user?user_id=1021820442510802945": "https://www.furaffinity.net/user/lottieloveart",
        "https://www.furaffinity.net/stats/duskmoor/submissions/": "https://www.furaffinity.net/user/duskmoor",
    },
    FuraffinityImageUrl: {
        "https://d.furaffinity.net/art/iwbitu/1650222955/1650222955.iwbitu_yubi.jpg": "https://d.furaffinity.net/art/iwbitu/1650222955/1650222955.iwbitu_yubi.jpg",
        "https://t.furaffinity.net/46821705@800-1650222955.jpg": "",

    },
    FuraffinityArtistImageUrl: {
        "https://a.furaffinity.net/1550854991/iwbitu.gif": "https://a.furaffinity.net/1550854991/iwbitu.gif",
    },
    FuraffinityPostUrl: {
        "https://www.furaffinity.net/view/46821705/": "https://www.furaffinity.net/view/46821705",
        "https://www.furaffinity.net/view/46802202/": "https://www.furaffinity.net/view/46802202",
        "https://www.furaffinity.net/full/46821705/": "https://www.furaffinity.net/view/46821705",
    },
}


generate_parsing_suite(urls)
