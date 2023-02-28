from ward import test

from danboorutools.logical.extractors.pixiv import PixivArtistUrl, PixivImageUrl, PixivMeUrl, PixivPostUrl, PixivStaccUrl
from danboorutools.models.url import Url
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


@test("Scrape dead pixiv image", tags=["scraping", "pixiv", "asset", "dead"])
def test_dead_3() -> None:
    assert_url(
        url_type=PixivImageUrl,
        url="https://i.pximg.net/img-original/img/2022/10/06/13/42/55/101721495_p0.png",
        url_properties=dict(post_id=101721495, page=0),
        is_deleted=True
    )


urls = {
    "https://i-f.pximg.net/img-original/img/2020/02/19/00/40/18/79584713_p0.png": "https://i-f.pximg.net/img-original/img/2020/02/19/00/40/18/79584713_p0.png",
    # "https://i.pximg.net/c/250x250_80_a2/img-master/img/2014/10/29/09/27/19/46785915_p0_square1200.jpg": "https://i.pximg.net/c/250x250_80_a2/img-master/img/2014/10/29/09/27/19/46785915_p0_square1200.jpg",
    # "https://i.pximg.net/c/360x360_70/custom-thumb/img/2022/03/08/00/00/56/96755248_p0_custom1200.jpg": "https://i.pximg.net/c/360x360_70/custom-thumb/img/2022/03/08/00/00/56/96755248_p0_custom1200.jpg",
    # "https://i.pximg.net/img-master/img/2014/10/03/18/10/20/46324488_p0_master1200.jpg": "https://i.pximg.net/img-master/img/2014/10/03/18/10/20/46324488_p0_master1200.jpg",
    "https://i.pximg.net/img-original/img/2014/10/03/18/10/20/46324488_p0.png": "https://i.pximg.net/img-original/img/2014/10/03/18/10/20/46324488_p0.png",
    "https://i.pximg.net/img-original/img/2019/05/27/17/59/33/74932152_ugoira0.jpg": "https://i.pximg.net/img-original/img/2019/05/27/17/59/33/74932152_ugoira0.jpg",
    "https://i.pximg.net/img-zip-ugoira/img/2016/04/09/14/25/29/56268141_ugoira1920x1080.zip": "https://i.pximg.net/img-zip-ugoira/img/2016/04/09/14/25/29/56268141_ugoira1920x1080.zip",

    # "https://i.pximg.net/img-inf/img/2014/09/11/00/16/59/45906923_s.jpg": "https://i.pximg.net/img-inf/img/2014/09/11/00/16/59/45906923_s.jpg",

    # "https://i.pximg.net/img25/img/nwqkqr/22218203.jpg": "https://i.pximg.net/img25/img/nwqkqr/22218203.jpg",

    "https://i.pximg.net/img-original/img/2018/03/30/10/50/16/67982747-04d810bf32ebd071927362baec4057b6_p0.png": "https://i.pximg.net/img-original/img/2018/03/30/10/50/16/67982747-04d810bf32ebd071927362baec4057b6_p0.png",

    "https://i.pximg.net/user-profile/img/2021/08/25/00/00/40/21290212_0374c372d602a6ec6b311764b0168a13_170.jpg": "https://i.pximg.net/user-profile/img/2021/08/25/00/00/40/21290212_0374c372d602a6ec6b311764b0168a13_170.jpg",

    # "https://i.pximg.net/c/600x600/novel-cover-master/img/2018/08/18/19/45/23/10008846_215387d3665210eed0a7cc564e4c93f3_master1200.jpg": "https://i.pximg.net/c/600x600/novel-cover-master/img/2018/08/18/19/45/23/10008846_215387d3665210eed0a7cc564e4c93f3_master1200.jpg",
    "https://i.pximg.net/novel-cover-original/img/2022/11/17/15/07/44/tei336490527346_a4ef4696530c4675fabef4b8e6e186c9.jpg": "https://i.pximg.net/novel-cover-original/img/2022/11/17/15/07/44/tei336490527346_a4ef4696530c4675fabef4b8e6e186c9.jpg",
    "https://i.pximg.net/img96/img/masao_913555/novel/4472318.jpg": "https://i.pximg.net/img96/img/masao_913555/novel/4472318.jpg",

    "https://i.pximg.net/background/img/2021/11/19/01/48/36/3767624_473f1bc024142eef43c80d2b0061b25a.jpg": "https://i.pximg.net/background/img/2021/11/19/01/48/36/3767624_473f1bc024142eef43c80d2b0061b25a.jpg",
    "https://i.pximg.net/workspace/img/2016/06/23/13/21/30/3968542_1603f967a310f7b03629b07a8f811c13.jpg": "https://i.pximg.net/workspace/img/2016/06/23/13/21/30/3968542_1603f967a310f7b03629b07a8f811c13.jpg",


    "https://www.pixiv.net/u/9202877": "https://www.pixiv.net/en/users/9202877",
    "https://www.pixiv.net/users/9202877": "https://www.pixiv.net/en/users/9202877",
    "https://www.pixiv.net/users/76567/novels": "https://www.pixiv.net/en/users/76567",
    "https://www.pixiv.net/users/39598149/illustrations?p=1": "https://www.pixiv.net/en/users/39598149",
    "https://www.pixiv.net/user/13569921/series/81967": "https://www.pixiv.net/en/users/13569921",
    "https://www.pixiv.net/en/users/9202877": "https://www.pixiv.net/en/users/9202877",
    "https://www.pixiv.net/en/users/76567/novels": "https://www.pixiv.net/en/users/76567",

    "https://www.pixiv.net/member.php?id=339253": "https://www.pixiv.net/en/users/339253",
    "http://www.pixiv.net/novel/member.php?id=76567": "https://www.pixiv.net/en/users/76567",

    # "http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_64x64.jpg": "http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_64x64.jpg",
    # "http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_s.png": "http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_s.png",

    "http://i3.pixiv.net/img-original/img/2016/05/30/11/53/26/57141110_p0.jpg": "http://i3.pixiv.net/img-original/img/2016/05/30/11/53/26/57141110_p0.jpg",

    # "https://www.pixiv.net/en/artworks/83371546#1": "https://www.pixiv.net/en/artworks/83371546#1",
    # "https://www.pixiv.net/en/artworks/92045058#big_11": "https://www.pixiv.net/en/artworks/92045058#big_11",

    # "http://i1.pixiv.net/img07/img/pasirism/18557054_p1.png": "http://i1.pixiv.net/img07/img/pasirism/18557054_p1.png",
    # "http://i2.pixiv.net/img18/img/evazion/14901720.png": "http://i2.pixiv.net/img18/img/evazion/14901720.png",

    # "https://img17.pixiv.net/yellow_rabbit/3825834.jpg": "https://img17.pixiv.net/yellow_rabbit/3825834.jpg",
    # "http://img18.pixiv.net/img/evazion/14901720.png": "http://img18.pixiv.net/img/evazion/14901720.png",
    # "http://img04.pixiv.net/img/aenobas/20513642_big_p48.jpg": "http://img04.pixiv.net/img/aenobas/20513642_big_p48.jpg",

    "https://www.pixiv.net/en/artworks/46324488": "https://www.pixiv.net/en/artworks/46324488",
    "https://www.pixiv.net/artworks/46324488": "https://www.pixiv.net/en/artworks/46324488",
    "http://www.pixiv.net/i/18557054": "https://www.pixiv.net/en/artworks/18557054",

    "http://www.pixiv.net/member_illust.php?mode=medium&illust_id=18557054": "https://www.pixiv.net/en/artworks/18557054",
    "http://www.pixiv.net/member_illust.php?mode=big&illust_id=18557054": "https://www.pixiv.net/en/artworks/18557054",
    "http://www.pixiv.net/member_illust.php?mode=manga&illust_id=18557054": "https://www.pixiv.net/en/artworks/18557054",
    "http://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=18557054&page=1": "https://www.pixiv.net/en/artworks/18557054",
    "https://www.pixiv.net/index.php?mode=medium\u0026illust_id=612896": "https://www.pixiv.net/en/artworks/612896",

    "https://www.pixiv.net/en/artworks/unlisted/ntQchboUi1CsqMhDpo5j": "https://www.pixiv.net/en/artworks/unlisted/ntQchboUi1CsqMhDpo5j",

    "https://www.pixiv.net/stacc/noizave": "https://www.pixiv.net/stacc/noizave",
    "https://blog.pixiv.net/zerousagi/": "https://www.pixiv.net/stacc/zerousagi",

    "http://i2.pixiv.net/img14/profile/muta0083/4810758.jpg": "http://i2.pixiv.net/img14/profile/muta0083/4810758.jpg",

    "https://www.pixiv.net/requests/7829": "https://www.pixiv.net/requests/7829",

    "https://www.pixiv.net/novel/show.php?id=8465454": "https://www.pixiv.net/novel/show.php?id=8465454",
    "https://www.pixiv.net/novel/show.php?id=10008846#8": "https://www.pixiv.net/novel/show.php?id=10008846",

    "https://www.pixiv.net/novel/series/436782": "https://www.pixiv.net/novel/series/436782",

    "http://i4.pixiv.net/img96/img/masao_913555/novel/4472318.jpg": "http://i4.pixiv.net/img96/img/masao_913555/novel/4472318.jpg",

    "http://www.pixiv.me/noizave": "https://pixiv.me/noizave",
    "https://pixiv.cc/zerousagi": "https://www.pixiv.net/stacc/zerousagi",
    "http://pixiv.cc/ecirtaeb/archives/2434154.html": "https://www.pixiv.net/stacc/ecirtaeb",
}

for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
