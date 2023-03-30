from danboorutools.logical.urls.potofu import PotofuArtistUrl
from tests.urls import assert_info_url, generate_parsing_suite

urls = {
    PotofuArtistUrl: {
        "https://potofu.me/158161163": "https://potofu.me/158161163",
    },
}


generate_parsing_suite(urls)

assert_info_url(
    "https://potofu.me/158161163",
    url_type=PotofuArtistUrl,
    url_properties=dict(user_id=158161163),
    related=[
        "https://158161163.tumblr.com",
        "https://marshmallow-qa.com/_158161163",
        "https://mobile.twitter.com/_158161163",
        "https://pawoo.net/@_158161163",
        "https://skeb.jp/@_158161163",
        "https://www.deviantart.com/suzzui",
        "https://www.pixiv.net/en/users/88293257",
    ],
    primary_names=["錫i", "suzzu"],
    secondary_names=[],
)
