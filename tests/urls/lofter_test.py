import pytest

from danboorutools.logical.urls.lofter import LofterArtistUrl, LofterImageUrl, LofterPostUrl, LofterRedirectArtistUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl, _TestRedirectUrl

urls = {
    LofterArtistUrl: {
        "https://www.lofter.com/front/blog/home-page/noshiqian": "https://noshiqian.lofter.com",
        "http://www.lofter.com/app/xiaokonggedmx": "https://xiaokonggedmx.lofter.com",
        "http://www.lofter.com/blog/semblance": "https://semblance.lofter.com",
        "http://gengar563.lofter.com": "https://gengar563.lofter.com",

    },
    LofterPostUrl: {
        "https://gengar563.lofter.com/post/1e82da8c_1c98dae1b": "https://gengar563.lofter.com/post/1e82da8c_1c98dae1b",
    },
    LofterImageUrl: {
        "https://imglf3.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJSzFCWFlnUWgzb01DcUdpT1lreG5yQjJVMkhGS09HNGR3PT0.png?imageView&thumbnail=1680x0&quality=96&stripmeta=0": "https://imglf3.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJSzFCWFlnUWgzb01DcUdpT1lreG5yQjJVMkhGS09HNGR3PT0.png",
        "https://imglf3.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJSzFCWFlnUWgzb01DcUdpT1lreG5yQjJVMkhGS09HNGR3PT0.png": "https://imglf3.lf127.net/img/S1d2QlVsWkJhSW1qcnpIS0ZSa3ZJSzFCWFlnUWgzb01DcUdpT1lreG5yQjJVMkhGS09HNGR3PT0.png",
        "http://imglf0.nosdn.127.net/img/cHl3bXNZdDRaaHBnNWJuN1Y4OXBqR01CeVBZSVNmU2FWZWtHc1h4ZTZiUGxlRzMwZnFDM1JnPT0.jpg": "http://imglf0.nosdn.127.net/img/cHl3bXNZdDRaaHBnNWJuN1Y4OXBqR01CeVBZSVNmU2FWZWtHc1h4ZTZiUGxlRzMwZnFDM1JnPT0.jpg",

        # http://gacha.nosdn.127.net/0a47df61008b46668a56d2f9e4b3c0b3.png?axis=0\u0026enlarge=1\u0026imageView\u0026quality=100\u0026type=png
    },
    LofterRedirectArtistUrl: {
        "https://www.lofter.com/mentionredirect.do?blogId=1890789": "https://www.lofter.com/mentionredirect.do?blogId=1890789",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestLofterArtistUrl1(_TestArtistUrl):
    url_string = "https://lbgu1.lofter.com/"
    url_type = LofterArtistUrl
    url_properties = dict(username="lbgu1")
    primary_names = ["LB"]
    secondary_names = ["lbgu1"]
    related = []


class TestLofterArtistUrl2(_TestArtistUrl):
    url_string = "https://jiaojiaojiazuzy.lofter.com/"
    url_type = LofterArtistUrl
    url_properties = dict(username="jiaojiaojiazuzy")
    primary_names = ["佼佼家族"]
    secondary_names = ["jiaojiaojiazuzy"]
    related = []


class TestLofterArtistUrl3(_TestArtistUrl):
    url_string = "https://chaodazu.lofter.com/"
    url_type = LofterArtistUrl
    url_properties = dict(username="chaodazu")
    primary_names = ["老祖祖"]
    secondary_names = ["chaodazu"]
    related = []


class TestLofterArtistUrl4(_TestArtistUrl):
    url_string = "https://asdfart.lofter.com/"
    url_type = LofterArtistUrl
    url_properties = dict(username="asdfart")
    primary_names = []
    secondary_names = ["asdfart"]
    related = []
    is_deleted = True


class TestLofterRedirectArtistUrl(_TestRedirectUrl):
    url_string = "https://www.lofter.com/mentionredirect.do?blogId=1890789"
    url_type = LofterRedirectArtistUrl
    url_properties = dict(blog_id=1890789)
    redirects_to = "https://sakuraihum.lofter.com/"
