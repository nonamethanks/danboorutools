import pytest

from danboorutools.logical.urls import mixi as m
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    m.MixiProfileUrl: {
        "http://mixi.jp/show_profile.pl?id=31861634": "https://mixi.jp/show_friend.pl?id=31861634",
        "https://mixi.jp/show_friend.pl?id=31861634": "https://mixi.jp/show_friend.pl?id=31861634",
        "https://photo.mixi.jp/home.pl?owner_id=28854449": "https://mixi.jp/show_friend.pl?id=28854449",
        "http://mixi.jp/show_friend.pl?id=610331/": "https://mixi.jp/show_friend.pl?id=610331",
        "http://mixi.jp/list_album.pl?id=541227": "https://mixi.jp/show_friend.pl?id=541227",
        "http://video.mixi.jp/list_video.pl?owner_id=26757304": "https://mixi.jp/show_friend.pl?id=26757304",
        "https://mixi.jp/list_diary.pl?id=396054": "https://mixi.jp/show_friend.pl?id=396054",
        "http://mixi.jp/show_friend.pl?pt=261193": "https://mixi.jp/show_friend.pl?id=261193",
        "http://open.mixi.jp/user/1105979/diary": "https://mixi.jp/show_friend.pl?id=1105979",
        "http://mixi.jp/list_voice.pl?owner_id=51749323": "https://mixi.jp/show_friend.pl?id=51749323",
        "https://mixi.jp/login.pl?next_url=https://mixi.jp/show_friend.pl?id=5383767": "https://mixi.jp/show_friend.pl?id=5383767",
        "http://id.mixi.jp/35830124": "https://mixi.jp/show_friend.pl?id=35830124",
    },
    m.MixiVideoUrl: {
        "https://video.mixi.jp/list_video.pl?id=730282": "https://video.mixi.jp/list_video.pl?id=730282",
    },
    m.MixiCommunityUrl: {
        "http://mixi.jp/view_community.pl?id=1958589": "https://mixi.jp/view_community.pl?id=1958589",
    },
    m.MixiCommunityPostUrl: {
        "https://mixi.jp/view_bbs.pl?comm_id=1379510&id=84865022": "https://mixi.jp/view_bbs.pl?id=84865022&comm_id=1379510",
    },
    m.MixiApplicationUrl: {
        "http://mixi.jp/run_appli.pl?id=3774&owner_id=1078055": "https://mixi.jp/run_appli.pl?id=3774&owner_id=1078055",
    },
    m.MixiPageUrl: {
        "http://page.mixi.jp/view_page.pl?page_id=74113": "https://page.mixi.jp/view_page.pl?page_id=74113",
    },
    m.MixiAlbumUrl: {
        "https://photo.mixi.jp/view_album.pl?album_id=8322560&owner_id=25119233": "https://photo.mixi.jp/view_album.pl?album_id=8322560&owner_id=25119233",
    },
    m.MixiPhotoUrl: {
        "https://photo.mixi.jp/view_photo.pl?photo_id=2354695773&owner_id=161740": "https://photo.mixi.jp/view_photo.pl?photo_id=2354695773&owner_id=161740",
    },
    m.MixiDiaryUrl: {
        "http://mixi.jp/view_diary.pl?id=237180079&owner_id=3295441": "https://mixi.jp/view_diary.pl?id=237180079&owner_id=3295441",
        "http://open.mixi.jp/user/1105979/diary/1967636848": "https://mixi.jp/view_diary.pl?id=1967636848&owner_id=1105979",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestMixiProfileUrl(_TestArtistUrl):
    url_string = "https://mixi.jp/show_friend.pl?id=31861634"
    url_type = m.MixiProfileUrl
    url_properties = dict(profile_id=31861634)
    primary_names = ["えんちー"]
    secondary_names = []
    related = ["http://mixi.jp/view_diary.pl?guid=ON&id=1558166939&owner_id=31861634",
               "http://photo.mixi.jp/view_album.pl?album_id=422201184507583&owner_id=31861634"]
