import pytest

from danboorutools.logical.urls.circle_ms import CircleMsCircleUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_info_test

urls = {
    CircleMsCircleUrl: {
        "https://portal.circle.ms/Circle/Index/10315665": "https://portal.circle.ms/Circle/Index/10315665",
        "http://portal.circle.ms/circle/index/10022032/": "https://portal.circle.ms/Circle/Index/10022032",
        "http://webcatalog.circle.ms/Perma/Circle/10217247": "https://portal.circle.ms/Circle/Index/10217247",
        "http://c10011401.circle.ms/oc/CircleProfile.aspx": "https://portal.circle.ms/Circle/Index/10011401",
        "https://webcatalog-free.circle.ms/Circle/14232303": "https://portal.circle.ms/Circle/Index/14232303",
        "http://c10067422.circle.ms/cr/CircleProfile.aspx": "https://portal.circle.ms/Circle/Index/10067422",
        "http://c10024411.circle.ms/cr/CircleHome.aspx": "https://portal.circle.ms/Circle/Index/10024411",
        "http://c10025912.circle.ms/oc/CircleImages.aspx": "https://portal.circle.ms/Circle/Index/10025912",
        "http://myportal.circle.ms/CircleInfo/Menu/10251988": "https://portal.circle.ms/Circle/Index/10251988",
        "http://c10003509.circle.ms/oc/circleprofile.aspx": "https://portal.circle.ms/Circle/Index/10003509",
        "http://c10014108.circle.ms/pics.aspx?PCODE=566388-04-1\u0026PTHUMB=false": "https://portal.circle.ms/Circle/Index/10014108",
        "http://c10001034.circle.ms/oc/pp/Paper.aspx?CPID=12505": "https://portal.circle.ms/Circle/Index/10001034",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_info_url_1():
    generate_info_test(
        url_string="https://portal.circle.ms/Circle/Index/10217247",
        url_type=CircleMsCircleUrl,
        url_properties=dict(circle_id=10217247),
        primary_names=["ツバサ"],
        secondary_names=[],
        related=[
            "http://www.abchipika.jp",
            "https://twitter.com/winglet283",
            "https://www.nicovideo.jp/user/2928869",
            "https://www.pixiv.net/en/users/29077",
        ],
    )


def test_info_url_2():
    generate_info_test(
        url_string="https://portal.circle.ms/Circle/Index/10217247123",
        url_type=CircleMsCircleUrl,
        url_properties=dict(circle_id=10217247123),
        primary_names=[],
        secondary_names=[],
        related=[],
        is_deleted=True,
    )
