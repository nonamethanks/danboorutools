from danboorutools.logical.urls.kakuyomu import KakuyomuArtistUrl, KakuyomuPostUrl
from tests.urls import assert_artist_url, assert_post_url, generate_parsing_suite

urls = {
    KakuyomuArtistUrl: {
        "http://kakuyomu.jp/users/warugi871": "https://kakuyomu.jp/users/warugi871",
    },
    KakuyomuPostUrl: {
        "https://kakuyomu.jp/works/4852201425154874772": "https://kakuyomu.jp/works/4852201425154874772",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    url="http://kakuyomu.jp/users/warugi871",
    url_type=KakuyomuArtistUrl,
    url_properties=dict(username="warugi871"),
    primary_names=["羽流木はない"],
    secondary_names=["warugi871"],
    related=["https://twitter.com/warugi871"],
)


assert_post_url(
    url="https://kakuyomu.jp/works/16817330659778429227",
    url_type=KakuyomuPostUrl,
    url_properties=dict(post_id=16817330659778429227),
    gallery="https://kakuyomu.jp/users/parantica_sita",
)
