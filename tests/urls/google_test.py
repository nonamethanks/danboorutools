import pytest

from danboorutools.logical.urls import google as g
from danboorutools.logical.urls import google_drive as gd
from danboorutools.logical.urls import google_photos as gph
from danboorutools.logical.urls import google_plus as gpl
from danboorutools.logical.urls import google_sites as gs
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test, generate_info_test, generate_post_test

urls = {
    gs.GoogleSitesArtistUrl: {
        "http://sites.google.com/site/ondineformula/": "https://sites.google.com/site/ondineformula",
        "https://sites.google.com/view/mustardsfm/home-page": "https://sites.google.com/site/mustardsfm",
        "https://sites.google.com/view/morionairlines/": "https://sites.google.com/site/morionairlines",
    },
    gs.GoogleSitesPostUrl: {
        "http://sites.google.com/site/ayakusi/_/rsrc/1304440299815/codama/touhoku-ouen2/": "https://sites.google.com/site/ayakusi/_/rsrc/1304440299815/codama/touhoku-ouen2",
    },
    gs.GoogleSitesImageUrl: {
        "https://sites.google.com/site/chikuwabgold/home/eva2.jpg": "",
    },
    g.GooglePicasaArtistUrl: {
        "http://picasaweb.google.com/106359455091421702960": "https://picasaweb.google.com/106359455091421702960",
        "http://picasaweb.google.com/kinkuro1": "https://picasaweb.google.com/kinkuro1",
    },
    g.GooglePicasaPostUrl: {
        "https://picasaweb.google.com/lh/photo/gHF5yy2jvEjtkisvLV8m-w?feat=embedwebsite": "https://picasaweb.google.com/lh/photo/gHF5yy2jvEjtkisvLV8m-w",
    },
    g.GoogleProfilesUrl: {
        "http://profiles.google.com/109331443954535276684/about": "https://profiles.google.com/109331443954535276684",
        "http://www.google.com/profiles/hanosukeworks": "https://profiles.google.com/hanosukeworks",
    },
    g.GooglePlayDeveloperUrl: {
        "http://play.google.com/store/apps/developer?id=K2000": "https://play.google.com/store/apps/developer?id=K2000",
        "http://play.google.com/store/apps/dev?id=8287620048499474172": "https://play.google.com/store/apps/dev?id=8287620048499474172",
    },
    gd.GoogleDriveFolderUrl: {
        "https://drive.google.com/drive/folders/1a3ZpLWI8NqStnH6bTmcY7d5GhnV8DiQR": "https://drive.google.com/drive/folders/1a3ZpLWI8NqStnH6bTmcY7d5GhnV8DiQR",
        "https://drive.google.com/folderview?id=0Bz5iC3UiWJaGN2xWOERaYXotM28&usp=sharing": "https://drive.google.com/drive/folders/0Bz5iC3UiWJaGN2xWOERaYXotM28",
        "https://drive.google.com/drive/u/0/folders/1-1toeBYF_ZJ7Jgnjf7SVxHDCKkh9L89U": "https://drive.google.com/drive/folders/1-1toeBYF_ZJ7Jgnjf7SVxHDCKkh9L89U",
        "https://drive.google.com/open?id=1L3y8MqyDUhZlHi8FzxRzdGhIlerubnej": "https://drive.google.com/drive/folders/1L3y8MqyDUhZlHi8FzxRzdGhIlerubnej",
        "https://drive.google.com/drive/mobile/folders/0B2876gCiqJjGQXhfZlRVd2JJUmM/119Rg9qtzcY2c6_zLLVKE5aNqn6wsLQkR?resourcekey=0--YPuu7q99JeKiHG2aFFduw&usp=sharing&sort=15&direction=d": "https://drive.google.com/drive/folders/119Rg9qtzcY2c6_zLLVKE5aNqn6wsLQkR",
    },
    gd.GoogleDriveFileUrl: {
        "https://drive.google.com/file/d/1zItUaRCYpJJz3Rbr0JClK24oQj4LciOP/view": "https://drive.google.com/file/d/1zItUaRCYpJJz3Rbr0JClK24oQj4LciOP/view",
        "https://drive.google.com/uc?export=download&id=1WpHYbFE8vNL6jzcjXbMf5sVuQKzj7dxq": "https://drive.google.com/file/d/1WpHYbFE8vNL6jzcjXbMf5sVuQKzj7dxq/view",
    },
    gpl.GooglePlusArtistUrl: {
        "https://plus.google.com/+KazuhiroMizushima/": "https://plus.google.com/+KazuhiroMizushima",
        "https://plus.google.com/u/0/+rtil": "https://plus.google.com/+rtil",
        "https://plus.google.com/u/0/117264078940479654527": "https://plus.google.com/117264078940479654527",
        "http://plus.google.com/111867792020765799161/posts": "https://plus.google.com/111867792020765799161",
        "https://plus.google.com/u/2/113625286503557181249": "https://plus.google.com/113625286503557181249",
        "http://plus.google.com/photos/115260099196768427303/albums/posts": "https://plus.google.com/115260099196768427303",
        "http://plus.google.com/u/0/114100282763774851465/posts": "https://plus.google.com/114100282763774851465",
        "http://plus.google.com/photos/+teracykojima/albums": "https://plus.google.com/+teracykojima",
        "http://plus.google.com/u/0/110532977796437073008/photos": "https://plus.google.com/110532977796437073008",
        "http://plus.google.com/photos/102433630352141229500/albums/5443277998013510145": "https://plus.google.com/102433630352141229500",
        "http://plus.google.com/u/0/photos/+ikariyaashita/albums/6258748402112039089": "https://plus.google.com/+ikariyaashita",
        "http://google.com/+thedarkmangaka": "https://plus.google.com/+thedarkmangaka",
        "https://plus.google.com/u/0/b/115763191749244545325/+ilaBarattolo": "https://plus.google.com/+ilaBarattolo",
        "https://plus.google.com/u/0/b/115763191749244545325/102486819006366238576": "https://plus.google.com/115763191749244545325",
        "https://plus.google.com/photos/113088469849270210438/albums/6321484260231620177/6321484261881248162": "https://plus.google.com/113088469849270210438",
    },
    gpl.GooglePlusPostUrl: {
        "https://plus.google.com/104032434106102166363/posts/ipBpMGJGwvx": "https://plus.google.com/104032434106102166363/posts/ipBpMGJGwvx",
        "https://plus.google.com/b/103804732399819310073/+TheWegeeMaster/posts/7F4CTCADh3u?pageId=103804732399819310073&pid=6200766528945844530&oid=103804732399819310073": "https://plus.google.com/+TheWegeeMaster/posts/7F4CTCADh3u",
    },
    gph.GooglePhotosFolderUrl: {
        "https://photos.google.com/share/AF1QipOsY2yG-tdGQkS1hXfBECdoAgjM-DtKv1K9OHCW6UGEdsQsA0f8kmXQlG48OEeN5w?key=YTExZi1aU2ZwbXIxU3c3em9FeWRzbkhtT3NjcnNn": "https://photos.google.com/share/AF1QipOsY2yG-tdGQkS1hXfBECdoAgjM-DtKv1K9OHCW6UGEdsQsA0f8kmXQlG48OEeN5w?key=YTExZi1aU2ZwbXIxU3c3em9FeWRzbkhtT3NjcnNn",
    },
    gph.GooglePhotosPhotoUrl: {
        "https://photos.google.com/photo/AF1QipM_y6EIrsILfA4vNSUCcH0kMbzAIXJVFYHCagl5": "",
    },

}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_artist_url_1():
    generate_artist_test(
        url_string="https://plus.google.com/+KazuhiroMizushima",
        url_type=gpl.GooglePlusArtistUrl,
        url_properties=dict(user_id="+KazuhiroMizushima"),
        primary_names=[],
        secondary_names=["KazuhiroMizushima"],
        related=[],
        is_deleted=True,
    )


def test_artist_url_2():
    generate_artist_test(
        url_string="https://plus.google.com/115763191749244545325",
        url_type=gpl.GooglePlusArtistUrl,
        url_properties=dict(user_id="115763191749244545325"),
        primary_names=[],
        secondary_names=[],
        related=[],
        is_deleted=True,
    )


def test_artist_url_3():
    generate_info_test(
        url_string="http://profiles.google.com/mutex.skyhigh/about",
        url_type=g.GoogleProfilesUrl,
        url_properties=dict(username="mutex.skyhigh"),
        primary_names=[],
        secondary_names=["mutex.skyhigh"],
        related=[],
        is_deleted=True,
    )


def test_post_url_1():
    generate_post_test(
        url_string="https://plus.google.com/u/0/b/115763191749244545325/102486819006366238576",
        url_type=gpl.GooglePlusPostUrl,
        url_properties=dict(user_id="115763191749244545325", post_id=102486819006366238576),
        gallery="https://plus.google.com/115763191749244545325",
        is_deleted=True,
    )
