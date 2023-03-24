from danboorutools.logical.urls.tw6 import Tw6ArtistUrl, Tw6CharacterUrl, Tw6ImageUrl, Tw6PostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    Tw6ArtistUrl: {
        "https://tw6.jp/gallery/master/?master_id=05344": "https://tw6.jp/gallery/master/?master_id=5344",
    },
    Tw6ImageUrl: {
        "https://cdn.tw6.jp/i/tw6/origin/3135/1085611_f31358_totalbody.png": "https://cdn.tw6.jp/i/tw6/origin/3135/1085611_f31358_totalbody.png",
        "https://cdn.tw6.jp/i/tw6/combined_origin/0258/1185475_f02583_totalbody.jpg": "https://cdn.tw6.jp/i/tw6/combined_origin/0258/1185475_f02583_totalbody.jpg",
        "https://cdn.tw6.jp/i/tw6/basic/0985/840921_f09857_totalbody.jpg": "https://cdn.tw6.jp/i/tw6/basic/0985/840921_f09857_totalbody.jpg",
    },
    Tw6PostUrl: {
        "https://tw6.jp/gallery/?id=135910": "https://tw6.jp/gallery/?id=135910",
        "https://tw6.jp/gallery/?id=0135910": "https://tw6.jp/gallery/?id=135910",
        "https://tw6.jp/gallery/combine/6003": "https://tw6.jp/gallery/?id=6003",
    },
    Tw6CharacterUrl: {
        "https://tw6.jp/character/status/f01521": "https://tw6.jp/character/status/f01521",
    },
}


generate_parsing_suite(urls)


assert_artist_url(
    "https://tw6.jp/gallery/master/?master_id=05344",
    url_type=Tw6ArtistUrl,
    url_properties=dict(user_id=5344),
    primary_names=["いもーす"],
    secondary_names=[],
    related=[],
)
