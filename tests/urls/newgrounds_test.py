import pytest

from danboorutools.logical.urls import newgrounds as ns
from tests.helpers.parsing import generate_parsing_test

urls = {
    ns.NewgroundsArtistUrl: {
        "https://natthelich.newgrounds.com": "https://natthelich.newgrounds.com",
        "https://natthelich.newgrounds.com/art/": "https://natthelich.newgrounds.com",
    },
    ns.NewgroundsPostUrl: {

        "https://www.newgrounds.com/art/view/puddbytes/costanza-at-bat": "https://www.newgrounds.com/art/view/puddbytes/costanza-at-bat",
        "https://www.newgrounds.com/art/view/natthelich/fire-emblem-marth-plus-progress-pic": "https://www.newgrounds.com/art/view/natthelich/fire-emblem-marth-plus-progress-pic",
    },
    ns.NewgroundsVideoPostUrl: {
        "https://www.newgrounds.com/portal/video/536659": "https://www.newgrounds.com/portal/view/536659",
        "https://www.newgrounds.com/portal/view/536659": "https://www.newgrounds.com/portal/view/536659",
    },
    ns.NewgroundsDumpUrl: {

        "https://www.newgrounds.com/dump/item/ff72b3c77a959a8cca07f92d28f5d6ce": "https://www.newgrounds.com/dump/item/ff72b3c77a959a8cca07f92d28f5d6ce",
        "https://www.newgrounds.com/dump/download/ff72b3c77a959a8cca07f92d28f5d6ce": "https://www.newgrounds.com/dump/item/ff72b3c77a959a8cca07f92d28f5d6ce",
    },
    ns.NewgroundsAssetUrl: {
        "https://art.ngfiles.com/images/1254000/1254722_natthelich_pandora.jpg": "https://art.ngfiles.com/images/1254000/1254722_natthelich_pandora.jpg",
        "https://art.ngfiles.com/images/1033000/1033622_natthelich_fire-emblem-marth-plus-progress-pic.png?f1569487181": "https://art.ngfiles.com/images/1033000/1033622_natthelich_fire-emblem-marth-plus-progress-pic.png",

        "https://art.ngfiles.com/thumbnails/1254000/1254985.png?f1588263349": "",

        "https://art.ngfiles.com/comments/57000/iu_57615_7115981.jpg": "https://art.ngfiles.com/comments/57000/iu_57615_7115981.jpg",

        "https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.1080p.mp4?1639666238": "https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.mp4",
        "https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.720p.mp4?1639666238": "https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.mp4",
        "https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.360p.mp4?1639666238": "https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.mp4",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
