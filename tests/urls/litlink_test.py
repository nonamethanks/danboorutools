from danboorutools.logical.urls.litlink import LitlinkUrl
from tests.urls import assert_info_url, generate_parsing_suite

urls = {
    LitlinkUrl: {
        "https://lit.link/en/hayato69link": "https://lit.link/hayato69link",
    },
}

generate_parsing_suite(urls)

assert_info_url(
    "https://lit.link/en/hayato69link",
    url_type=LitlinkUrl,
    url_properties=dict(username="hayato69link"),
    primary_names=["隼人ろっく"],
    secondary_names=["hayato69link"],
    related=[
        "https://assets.clip-studio.com/ja-jp/search?user=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8F&order=new",
        "https://bit.ly/3xcRBib",
        "https://line.me/R/ti/p/%40092hdnqj",
        "https://marshmallow-qa.com/hayato69rock",
        "https://skeb.jp/@hayato69rock",
        "https://skima.jp/profile?id=244678",
        "https://store.line.me/stickershop/author/1140847",
        "https://twitter.com/hashtag/%E3%82%AC%E3%83%81%E3%83%A3%E3%83%89%E3%83%AD%E3%83%83%E3%82%AF?src=hashtag_click&f=live",
        "https://twitter.com/hayato69_YT",
        "https://twitter.com/hayato69rock",
        "https://www.amazon.jp/hz/wishlist/ls/1O5XMOZHKWBE8?ref_=wl_share",
        "https://www.pixiv.net/users/374228",
        "https://www.youtube.com/channel/UCtKqZDgqH9QnxJYeF0GDReQ",
        "https://www.youtube.com/channel/UCtKqZDgqH9QnxJYeF0GDReQ",
        "https://www.youtube.com/results?search_query=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8Fch&sp=EgIIBA%253D%253D",
        "https://xfolio.jp/portfolio/hayato69",
        "https://xfolio.jp/portfolio/hayato69/free/33407",
        "https://youtube.com/playlist?list=PLcw27-K4pcr23t305PlCpIYvulr0m2Agu",
    ],
)
