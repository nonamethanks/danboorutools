from ward import test

from danboorutools.logical.extractors.pixiv import PixivArtistUrl, PixivImageUrl, PixivMeUrl, PixivPostUrl, PixivStaccUrl
from tests.extractors import assert_artist_url, assert_asset_url, assert_info_url, assert_post_url, assert_redirect_url, assert_url


@test("Scrape pixiv artist", tags=["scraping", "pixiv", "artist"])
def test_artist() -> None:
    assert_artist_url(
        url_type=PixivArtistUrl,
        url="https://www.pixiv.net/en/users/10183321/artworks",
        primary_names=["囬巾"],
        secondary_names=["2001sys", "pixiv 10183321"],
        related=["https://www.pixiv.net/stacc/2001sys", "https://huijin177.lofter.com",
                 "https://calamitail.fanbox.cc", "https://sketch.pixiv.net/@2001sys"],
        post_count=40,
        url_properties=dict(user_id=10183321),
        posts=["https://www.pixiv.net/en/artworks/95096202"],
    )


@test("Scrape pixiv post", tags=["scraping", "pixiv", "post"])
def test_post() -> None:
    assert_post_url(
        url_type=PixivPostUrl,
        url="https://www.pixiv.net/en/artworks/95096202",
        asset_count=7,
        score=2473,
        created_at="2021-12-28 14:53:00",
        url_properties=dict(post_id=95096202),
        assets=["https://i.pximg.net/img-original/img/2021/12/28/23/53/02/95096202_p6.png"],
    )


@test("Scrape pixiv asset", tags=["scraping", "pixiv", "asset"])
def test_asset() -> None:
    assert_asset_url(
        url_type=PixivImageUrl,
        url="https://i.pximg.net/img-original/img/2021/12/28/23/53/02/95096202_p6.png",
        created_at="2021-12-28 23:53:02",
        url_properties=dict(post_id=95096202),
        md5s=["2abae1fc2d8b52fc2a1d54d6654181c6"],
    )


@test("Scrape pixiv stacc", tags=["scraping", "pixiv", "info"])
def test_info() -> None:
    assert_info_url(
        url_type=PixivStaccUrl,
        url="https://www.pixiv.net/stacc/982430143",
        url_properties=dict(stacc="982430143"),
        related=["https://www.pixiv.net/en/users/14761279"],
        primary_names=[],
        secondary_names=["982430143"],
    )


@test("Scrape pixiv me", tags=["scraping", "pixiv", "redirect"])
def test_redirect() -> None:
    assert_redirect_url(
        url_type=PixivMeUrl,
        url="https://www.pixiv.me/982430143",
        url_properties=dict(stacc="982430143"),
        redirects_to="https://www.pixiv.net/en/users/14761279"
    )


@test("Scrape dead pixiv artist", tags=["scraping", "pixiv", "artist", "dead"])
def test_dead_1() -> None:
    assert_url(
        url_type=PixivArtistUrl,
        url="https://www.pixiv.net/en/users/1",
        url_properties=dict(user_id=1),
        is_deleted=True
    )


@test("Scrape dead pixiv post", tags=["scraping", "pixiv", "post", "dead"])
def test_dead_2() -> None:
    assert_url(
        url_type=PixivPostUrl,
        url="https://www.pixiv.net/en/artworks/1",
        url_properties=dict(post_id=1),
        is_deleted=True
    )
