from danboorutools.logical.urls.behance import BehanceArtistUrl, BehancePostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    BehanceArtistUrl: {
        "https://www.behance.net/kienphongtran/sourcefiles": "https://www.behance.net/kienphongtran",
        "http://www.behance.net/sparklingthunder": "https://www.behance.net/sparklingthunder",
    },
    BehancePostUrl: {
        "https://www.behance.net/gallery/83538125/The-Saiyan-Prince-Pitch": "https://www.behance.net/gallery/83538125/The-Saiyan-Prince-Pitch",
        "https://www.behance.net/gallery/41416703/F-A-N-A-R-T/modules/249943521": "https://www.behance.net/gallery/41416703/F-A-N-A-R-T",
    },
    # BehanceImageUrl: {
    # },
}


generate_parsing_suite(urls)


assert_artist_url(
    "https://www.behance.net/kienphongtran",
    url_type=BehanceArtistUrl,
    url_properties=dict(username="kienphongtran"),
    primary_names=["Kien Phong Tran"],
    secondary_names=["kienphongtran"],
    related=[
        "http://twitter.com/KienPhong_Tran",
        "http://youtube.com/channel/UCxw3WZ7N63dYExDwbZbHvqg",
        "http://instagram.com/phng_11.02",
    ],
)
