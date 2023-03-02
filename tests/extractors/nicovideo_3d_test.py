from danboorutools.logical.extractors import nicovideo_3d as n3
from tests.extractors import generate_parsing_suite

urls = {
    n3.Nicovideo3dArtistUrl: {
        "https://3d.nicovideo.jp/users/109584": "https://3d.nicovideo.jp/users/109584",
        "https://3d.nicovideo.jp/users/29626631/works": "https://3d.nicovideo.jp/users/29626631",
        "https://3d.nicovideo.jp/u/siobi": "https://3d.nicovideo.jp/u/siobi",
    },
    n3.Nicovideo3dPostUrl: {
        "https://3d.nicovideo.jp/works/td28606": "https://3d.nicovideo.jp/works/td28606",
    },
}

generate_parsing_suite(urls)
