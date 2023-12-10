import pytest

from danboorutools.logical.urls.skima import SkimaArtistUrl, SkimaGalleryUrl, SkimaImageUrl, SkimaItemUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    SkimaArtistUrl: {
        "https://skima.jp/profile?id=244678": "https://skima.jp/profile?id=244678",
        "http://skima.jp/u/id21469/": "https://skima.jp/profile?id=21469",
        "https://skima.jp/profile/commissions?id=32742": "https://skima.jp/profile?id=32742",
        "https://skima.jp/u/id13356/まで": "https://skima.jp/profile?id=13356",
    },
    SkimaItemUrl: {
        "http://skima.jp/item/detail/?item_id=4661/": "https://skima.jp/item/detail?item_id=4661",
        "https://skima.jp/item/detail?item_id=217317": "https://skima.jp/item/detail?item_id=217317",
    },
    SkimaGalleryUrl: {
        "https://skima.jp/gallery?id=37282": "https://skima.jp/gallery?id=37282",
    },
    SkimaImageUrl: {
        "https://cdn-common.skima.jp/item/180/812/1180812/showcase-ff069e42591011ee6efc95907df64dbe-20230111222024.jpeg": "https://cdn-common.skima.jp/item/180/812/1180812/showcase-ff069e42591011ee6efc95907df64dbe-20230111222024.jpeg",

        "https://cdn-gallery.skima.jp/gallery/529/639/529639/tip-2c639a2be7c4c2984a7d3e894746dcac-20221016015859.jpeg": "",
        "https://cdn-gallery.skima.jp/gallery/529/639/529639/detail-1464a99fb503c40a3282e8d61681657d-20221016015858.jpeg": "",
        "https://cdn-gallery.skima.jp/gallery/529/639/529639/985db8d09a3386f1452ab0eb43e140f5-20221016015858.png": "https://cdn-gallery.skima.jp/gallery/529/639/529639/985db8d09a3386f1452ab0eb43e140f5-20221016015858.png",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestSkimaArtistUrl(_TestArtistUrl):
    url_string = "https://skima.jp/profile?id=244678"
    url_type = SkimaArtistUrl
    url_properties = dict(user_id=244678)
    primary_names = ["隼人ろっく"]
    secondary_names = []
    related = []
