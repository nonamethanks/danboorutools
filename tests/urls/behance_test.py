import pytest

from danboorutools.logical.urls.behance import BehanceArtistUrl, BehancePostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

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


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_artist_url_1():
    generate_artist_test(
        url_string="https://www.behance.net/kienphongtran",
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
