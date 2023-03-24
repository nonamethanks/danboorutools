from danboorutools.logical.urls.piapro import PiaproArtistUrl, PiaproPostUrl
from danboorutools.logical.urls.tumblr import TumblrArtistUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    PiaproArtistUrl: {
        "http://piapro.jp/ooyuko29": "https://piapro.jp/ooyuko29",
    },
    PiaproPostUrl: {
        "https://piapro.jp/t/Z8xi": "https://piapro.jp/t/Z8xi",
        "http://piapro.jp/content/7vmui67vj0uabnoc": "https://piapro.jp/content/7vmui67vj0uabnoc",
        "https://piapro.jp/t/01ix/20161127225144": "https://piapro.jp/t/01ix",
        "http://piapro.jp/a/content/?id=ncdt0qjsdpdb0lrk": "https://piapro.jp/content/ncdt0qjsdpdb0lrk",
    },
    TumblrArtistUrl: {
        "https://piapro.jp/jump/?url=https%3A%2F%2Fitoiss.tumblr.com": "https://itoiss.tumblr.com",
    },
}


generate_parsing_suite(urls)


assert_artist_url(
    "https://piapro.jp/woki_woki_chi",
    PiaproArtistUrl,
    url_properties=dict(username="woki_woki_chi"),
    primary_names=["町上ヨウ"],
    secondary_names=["woki_woki_chi"],
    related=["https://itoiss.tumblr.com"],
)
