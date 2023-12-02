import pytest

from danboorutools.logical.urls.tinami import TinamiArtistUrl, TinamiComicUrl, TinamiImageUrl, TinamiPostUrl
from tests.helpers.parsing import generate_parsing_test

urls = {
    TinamiArtistUrl: {
        "http://www.tinami.com/creator/profile/1624": "https://www.tinami.com/creator/profile/1624",
        "https://www.tinami.com/search/list?prof_id=1624": "https://www.tinami.com/creator/profile/1624",

        "http://www.tinami.com/profile/1182": "https://www.tinami.com/profile/1182",
        "http://www.tinami.jp/p/1182": "https://www.tinami.com/profile/1182",
    },
    TinamiImageUrl: {
        "https://img.tinami.com/illust/img/287/497c8a9dc60e6.jpg": "",
        "https://img.tinami.com/illust2/img/419/5013fde3406b9.jpg": "",
        "https://img.tinami.com/illust2/L/452/622f7aa336bf3.gif": "",
        "https://img.tinami.com/comic/naomao/naomao_001_01.jpg": "",
        "https://img.tinami.com/comic/naomao/naomao_002_01.jpg": "",
        "https://img.tinami.com/comic/naomao/naomao_topillust.gif": "",

    },
    TinamiPostUrl: {
        "https://www.tinami.com/view/461459": "https://www.tinami.com/view/461459",
        "https://www.tinami.com/view/tweet/card/461459": "https://www.tinami.com/view/461459",
    },
    TinamiComicUrl: {
        "http://www.tinami.com/comic/naomao/2": "https://www.tinami.com/comic/naomao/2",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
