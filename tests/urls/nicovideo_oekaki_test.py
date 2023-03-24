from danboorutools.logical.urls import nicovideo_oekaki as no
from tests.urls import generate_parsing_suite

urls = {
    no.NicovideoOekakiImageUrl: {
        "https://dic.nicovideo.jp/oekaki/176310.png": "https://dic.nicovideo.jp/oekaki/176310.png",
    },
    no.NicovideoOekakiPostUrl: {
        "https://dic.nicovideo.jp/oekaki_id/340604": "https://dic.nicovideo.jp/oekaki_id/340604",
    },
    no.NicovideoOekakiArtistUrl: {
        "https://dic.nicovideo.jp/u/11141663": "https://dic.nicovideo.jp/u/11141663",
        "https://dic.nicovideo.jp/r/u/10846063/2063955": "https://dic.nicovideo.jp/u/10846063",
    },
}


generate_parsing_suite(urls)
