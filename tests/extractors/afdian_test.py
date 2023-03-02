from ward import test

from danboorutools.logical.extractors.afdian import AfdianArtistImageUrl, AfdianArtistUrl, AfdianImageUrl, AfdianPostUrl
from tests.extractors import assert_artist_url, generate_parsing_suite

urls = {
    AfdianArtistUrl: {
        "https://afdian.net/a/mgong520": "https://afdian.net/a/mgong520",
        "https://afdian.net/@gggmmm": "https://afdian.net/a/gggmmm",
    },
    AfdianPostUrl: {
        "https://afdian.net/p/8d419ad28b3511ed830452540025c377": "https://afdian.net/p/8d419ad28b3511ed830452540025c377",
    },
    AfdianImageUrl: {
        "https://pic1.afdiancdn.com/user/8440cb74b10f11edb7ee52540025c377/common/e3e98041bbe0123906b4e949083616e7_w357_h357_s172.jpg?imageView2/3/w/320/h/180": "https://pic1.afdiancdn.com/user/8440cb74b10f11edb7ee52540025c377/common/e3e98041bbe0123906b4e949083616e7_w357_h357_s172.jpg",
        "https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/common/9dcd4e26f34d248a945e083570cf96f5_w2508_h3541_s3529.png": "https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/common/9dcd4e26f34d248a945e083570cf96f5_w2508_h3541_s3529.png",
        "https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/common/54c2aa732a3c1783b73fba1e2149f56d_w1170_h2532_s5894.png?imageView2/1/w/1500/h/400": "https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/common/54c2aa732a3c1783b73fba1e2149f56d_w1170_h2532_s5894.png",
    },
    AfdianArtistImageUrl: {
        "https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/avatar/b8affcddfae89977b4ea2f48cf4a6513_w5715_h3775_s1932.png?imageView2/1/w/120/h/120": "https://pic1.afdiancdn.com/user/3821112e647d11ed88e952540025c377/avatar/b8affcddfae89977b4ea2f48cf4a6513_w5715_h3775_s1932.png",
    },
}


generate_parsing_suite(urls)


@test("Scrape afdian artist", tags=["scraping", "afdian", "artist"])
def test_artist_1() -> None:
    assert_artist_url(
        url_type=AfdianArtistUrl,
        url="https://afdian.net/a/mgong520",
        url_properties=dict(username="mgong520"),
        primary_names=["尼德汞"],
        secondary_names=["mgong520"],
        related=[],
    )


@test("Scrape afdian artist with related urls", tags=["scraping", "afdian", "artist"])
def test_artist_2() -> None:
    assert_artist_url(
        url_type=AfdianArtistUrl,
        url="https://afdian.net/a/rubyredsims",
        url_properties=dict(username="rubyredsims"),
        primary_names=["RUBY RED SIMS"],
        secondary_names=["rubyredsims"],
        related=["http://www.patreon.com/rubyredsims"],
    )
