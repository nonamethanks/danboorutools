from ward import test

from danboorutools.logical.extractors.pixiv import PixivArtistUrl, PixivImageUrl, PixivPostUrl
from danboorutools.models.url import Url
from tests.extractors import assert_info_url, assert_redirect_url, generate_artist_test_suite

tests = generate_artist_test_suite(
    url_type=PixivArtistUrl,
    url="https://www.pixiv.net/en/users/10183321/artworks",
    names=['囬巾', '2001sys', 'pixiv #10183321'],
    related=["https://www.pixiv.net/stacc/2001sys", "https://huijin177.lofter.com"],
    normalized_url="https://www.pixiv.net/en/users/10183321",
    post_count=40,
    user_id=10183321,

    post=dict(
        url_type=PixivPostUrl,
        url="https://www.pixiv.net/en/artworks/95096202",
        asset_count=7,
        score=2473,
        created_at="2021-12-28 14:53:00",

        asset=dict(
            url_type=PixivImageUrl,
            url="https://i.pximg.net/img-original/img/2021/12/28/23/53/02/95096202_p6.png",
            created_at="2021-12-28 23:53:02",
            post_id=95096202,
            file_md5="2abae1fc2d8b52fc2a1d54d6654181c6",
        )
    )
)

for test_type, test_method in tests.items():
    @test(f"Scrape a pixiv {test_type}", tags=["scraping", "pixiv", test_type])  # pylint: disable=cell-var-from-loop
    def _(_test_method=test_method) -> None:
        _test_method()


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


@test("Deleted urls", tags=["scraping", "pixiv", "deleted"])
def test_deleted() -> None:
    assert Url.parse("https://www.pixiv.net/en/users/1").is_deleted
    assert Url.parse("https://www.pixiv.net/en/artworks/1").is_deleted
