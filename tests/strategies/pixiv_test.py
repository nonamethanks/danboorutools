from ward import test

from danboorutools.logical.strategies.pixiv import PixivArtistUrl, PixivImageUrl, PixivMeUrl, PixivPostUrl, PixivStaccUrl
from tests.strategies import (assert_artist_url, assert_asset_file, assert_asset_url, assert_info_url, assert_parsed, assert_post_url,
                              assert_post_url_from_string, assert_redirect_url)


@test("Parse pixiv urls", tags=["parsing", "pixiv"])
def pixiv_parsing_test() -> None:
    assert_parsed("https://www.pixiv.net/en/artworks/102960826", PixivPostUrl, 102960826)
    assert_parsed("https://www.pixiv.net/artworks/102960826", PixivPostUrl, 102960826)

    assert_parsed("https://i.pximg.net/img-zip-ugoira/img/2023/02/12/19/41/25/105314959_ugoira1920x1080.zip", PixivImageUrl, 105314959)
    assert_parsed("https://i.pximg.net/img-original/img/2021/08/08/01/34/48/91802726_p2.png", PixivImageUrl, 91802726)

    assert_parsed("https://www.pixiv.net/users/14761279", PixivArtistUrl, 14761279)
    assert_parsed("https://www.pixiv.net/stacc/982430143", PixivStaccUrl, 982430143)
    assert_parsed("https://www.pixiv.me/982430143", PixivMeUrl, 982430143)


@test("Scrape pixiv urls", tags=["scraping", "pixiv", "artist"])
def scrape_pixiv() -> None:
    artist_url = assert_artist_url(
        "https://www.pixiv.net/en/users/10183321/artworks",
        is_deleted=False,
        names=['囬巾', '2001sys', 'pixiv #10183321'],
        related=["https://www.pixiv.net/stacc/2001sys", "https://huijin177.lofter.com"],
        post_count=40
    )

    assert artist_url.posts[-1].normalized_url == "https://www.pixiv.net/en/artworks/44454703"
    assert "https://www.pixiv.net/en/artworks/104881527" in [u.normalized_url for u in artist_url.posts]

    post, = [p for p in artist_url.posts if p.id == "95096202"]

    post_url = "https://www.pixiv.net/en/artworks/95096202"
    post_creation_datetime = "2021-12-28 14:53:00"
    post_upload_datetime = "2021-12-28 14:53:02"   # why pixiv, fucking why
    image_revision_datetime = "2021-12-28 23:53:02"

    assert_post_url(
        post,
        normalized_url=post_url,
        gallery=artist_url,
        asset_count=7,
        score=2473,
        created_at=post_upload_datetime,
        check_from_string=False
    )
    assert_post_url_from_string(
        post_url,
        normalized_url=post_url,
        gallery=artist_url,
        asset_count=7,
        score=2473,
        created_at=post_creation_datetime,
    )

    asset = post.assets[-1]
    assert_asset_url(
        asset,
        normalized_url="https://i.pximg.net/img-original/img/2021/12/28/23/53/02/95096202_p6.png",
        gallery=artist_url,
        created_at=image_revision_datetime,
    )

    assert_asset_file(
        asset,
        ["2abae1fc2d8b52fc2a1d54d6654181c6"]
    )


@test("Scrape a pixiv stacc", tags=["scraping", "pixiv", "stacc"])
def scrape_stacc() -> None:
    assert_info_url(
        "https://www.pixiv.net/stacc/982430143",
        related=["https://www.pixiv.net/en/users/14761279"],
        names=["982430143"],
    )


@test("Scrape a pixiv .me", tags=["scraping", "pixiv", "me"])
def scrape_me() -> None:
    assert_redirect_url(
        "https://www.pixiv.me/982430143",
        redirect_to="https://www.pixiv.net/en/users/14761279"
    )
