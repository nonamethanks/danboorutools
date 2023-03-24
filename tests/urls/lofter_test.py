from danboorutools.logical.urls.lofter import LofterArtistUrl, LofterImageUrl, LofterPostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

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
}

generate_parsing_suite(urls)

assert_artist_url(
    "https://lbgu1.lofter.com/",
    url_type=LofterArtistUrl,
    url_properties=dict(username="lbgu1"),
    primary_names=["LB"],
    secondary_names=["lbgu1"],
    related=[],
)
