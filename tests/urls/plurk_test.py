from danboorutools.logical.urls.plurk import PlurkArtistUrl, PlurkImageUrl, PlurkPostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    PlurkArtistUrl: {
        "https://www.plurk.com/m/redeyehare": "https://www.plurk.com/redeyehare",
        "https://www.plurk.com/u/ddks2923": "https://www.plurk.com/ddks2923",
        "https://www.plurk.com/m/u/leiy1225": "https://www.plurk.com/leiy1225",
        "https://www.plurk.com/s/u/salmonroe13": "https://www.plurk.com/salmonroe13",
        "https://www.plurk.com/redeyehare": "https://www.plurk.com/redeyehare",
        "https://www.plurk.com/RSSSww/invite/4": "https://www.plurk.com/RSSSww",
    },
    PlurkImageUrl: {
        "https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg": "https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg",
        "https://images.plurk.com/mx_5wj6WD0r6y4rLN0DL3sqag.jpg": "https://images.plurk.com/5wj6WD0r6y4rLN0DL3sqag.jpg",

    },
    PlurkPostUrl: {
        "https://www.plurk.com/p/om6zv4": "https://www.plurk.com/p/om6zv4",
        "https://www.plurk.com/m/p/okxzae": "https://www.plurk.com/p/okxzae",
    },
}


generate_parsing_suite(urls)


assert_artist_url(
    "https://www.plurk.com/vivi890812",
    url_type=PlurkArtistUrl,
    url_properties=dict(username="vivi890812"),
    primary_names=["設後不理·犬勇者"],
    secondary_names=["vivi890812"],
    related=["https://her178542.pixnet.net",
             "https://home.gamer.com.tw/homeindex.php?owner=her682913",
             "https://www.pixiv.net/en/users/5253106"],
)
