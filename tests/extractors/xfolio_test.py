from danboorutools.logical.extractors.xfolio import XfolioArtistUrl, XfolioPostUrl
from tests.extractors import assert_artist_url, generate_parsing_suite

urls = {
    XfolioArtistUrl: {
        "https://xfolio.jp/portfolio/hayato69": "https://xfolio.jp/portfolio/hayato69",
        "https://xfolio.jp/portfolio/hayato69/free/33407": "https://xfolio.jp/portfolio/hayato69",
        "https://xfolio.jp/portfolio/hayato69/works": "https://xfolio.jp/portfolio/hayato69",
    },
    XfolioPostUrl: {
        "https://xfolio.jp/portfolio/Rei_0127/works/59931": "https://xfolio.jp/portfolio/Rei_0127/works/59931",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    "https://xfolio.jp/portfolio/hayato69",
    url_type=XfolioArtistUrl,
    url_properties=dict(username="hayato69"),
    primary_names=[],
    secondary_names=["hayato69"],
    related=[
        "https://www.pixiv.net/en/users/374228",
        "https://skeb.jp/@hayato69rock",
        "https://skima.jp/profile?id=244678",
    ],
)

assert_artist_url(
    "https://xfolio.jp/portfolio/negi_toro07",
    url_type=XfolioArtistUrl,
    url_properties=dict(username="negi_toro07"),
    primary_names=[],
    secondary_names=["negi_toro07"],
    related=[
        "https://twitter.com/negi_toro07",
        "https://www.instagram.com/negi_toro07/",
        "https://coconala.com/mypage/user",
        "https://skeb.jp/@negi_toro07",
        "https://skima.jp/profile?id=276250",
        "https://www.pixiv.net/users/14253416",
    ],
)
