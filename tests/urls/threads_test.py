from danboorutools.logical.urls.threads import ThreadsArtistUrl, ThreadsPostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    ThreadsArtistUrl: {
        "https://www.threads.net/@mawari5577": "https://www.threads.net/@mawari5577",
    },
    ThreadsPostUrl: {
        "https://www.threads.net/@saikou.jp/post/CvX2h-wJCTe.jpg": "https://www.threads.net/@saikou.jp/post/CvX2h-wJCTe",
        "https://www.threads.net/@saikou.jp/post/Cvabd9_PAbI": "https://www.threads.net/@saikou.jp/post/Cvabd9_PAbI",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    url="https://www.threads.net/@mawari5577",
    url_type=ThreadsArtistUrl,
    url_properties=dict(username="mawari5577"),
    primary_names=["海猫まわり"],
    secondary_names=["mawari5577"],
    related=["https://www.instagram.com/mawari5577/"],
)
