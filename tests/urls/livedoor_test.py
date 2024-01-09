import pytest

from danboorutools.logical.urls import livedoor as ld
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    ld.LivedoorBlogUrl: {
        "http://blog.livedoor.jp/pallet_box/": "http://blog.livedoor.jp/pallet_box/",
        "http://blog.livedoor.jp/okuirafan/search?q=momohiyaltuko0124": "http://blog.livedoor.jp/okuirafan/",
        "http://blog.livedoor.jp/jyugemu125/archives/cat_19311.html/": "http://blog.livedoor.jp/jyugemu125/",
        "http://blog.livedoor.jp/tokunaga3046/lite/": "http://blog.livedoor.jp/tokunaga3046/",
        "http://blog.livedoor.jp/geek/tag/サークル綿120パーセント": "http://blog.livedoor.jp/geek/",
        "http://blog.livedoor.jp/ribido88/imgs/8/7/": "http://blog.livedoor.jp/ribido88/",
        "http://image.blog.livedoor.jp/megadriv/imgs/": "http://blog.livedoor.jp/megadriv/",
    },
    ld.LiveDoorAaaArtistUrl: {
        "http://f49.aaa.livedoor.jp/~musashi/": "http://f49.aaa.livedoor.jp/~musashi/",
        "http://f28.aaa.livedoor.jp/~inohuru/images/": "http://f28.aaa.livedoor.jp/~inohuru/",
    },
    ld.LivedoorBlogArchiveUrl: {
        "http://blog.livedoor.jp/nobujyamira/archives/2167208.html/": "http://blog.livedoor.jp/nobujyamira/archives/2167208.html",
        "http://blog.livedoor.jp/dowman/archives/457319.htm": "http://blog.livedoor.jp/dowman/archives/457319.html",
        "http://blog.livedoor.jp/cosax/archives/44477406.html#more": "http://blog.livedoor.jp/cosax/archives/44477406.html",
        "http://blog.livedoor.jp/xxx0w/archives/51508589.html#comments": "http://blog.livedoor.jp/xxx0w/archives/51508589.html",
    },
    ld.LivedoorImageUrl: {
        "http://image.blog.livedoor.jp/chikubige/imgs/8/d/8dfb5d0c.gif": "",
        "http://image.blog.livedoor.jp/tiger501/0279e5a4.jpg": "",
        "http://image.blog.livedoor.jp/m-54_25833/imgs/0/e/0e33df5d-s.jpg": "",
        "http://image.blog.livedoor.jp/ayame_blog/imgs/5/e/5e3dd39d.JPG": "",
        "http://blog.livedoor.jp/akusenkuto/shishikokuchi01.jpg": "",
    },
    ld.LiveDoorAaaImageUrl: {
        "http://f20.aaa.livedoor.jp/~kusaren/img/nk/2007new.jpg": "",
        "http://f38.aaa.livedoor.jp/%7Eentzugel/diary/saku3-4.jpg": "",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestLivedoorArtistUrl1(_TestArtistUrl):
    url_string = "http://blog.livedoor.jp/pallet_box/"
    url_type = ld.LivedoorBlogUrl
    url_properties = dict(username="pallet_box")
    primary_names = []
    secondary_names = ["pallet_box"]
    related = []


class TestLivedoorArtistUrl2(_TestArtistUrl):
    url_string = "http://blog.livedoor.jp/rubbercorn5/"
    url_type = ld.LivedoorBlogUrl
    url_properties = dict(username="rubbercorn5")
    primary_names = []
    secondary_names = ["rubbercorn5"]
    related = []
    is_deleted = True


class TestLivedoorAaaUrl(_TestArtistUrl):
    url_string = "http://f49.aaa.livedoor.jp/~musashi/"
    url_type = ld.LiveDoorAaaArtistUrl
    url_properties = dict(username="musashi")
    primary_names = []
    secondary_names = ["musashi"]
    related = []
    is_deleted = True
