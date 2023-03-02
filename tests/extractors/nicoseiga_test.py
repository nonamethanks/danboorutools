from danboorutools.logical.extractors import nicoseiga as ns
from tests.extractors import generate_parsing_suite

urls = {
    ns.NicoSeigaIllustUrl: {
        "https://seiga.nicovideo.jp/seiga/im520647": "https://seiga.nicovideo.jp/seiga/im520647",
        "https://seiga.nicovideo.jp/seiga/im3521156": "https://seiga.nicovideo.jp/seiga/im3521156",
        "https://sp.seiga.nicovideo.jp/seiga/im3521156": "https://seiga.nicovideo.jp/seiga/im3521156",
        "https://sp.seiga.nicovideo.jp/seiga/#!/im6012363": "https://seiga.nicovideo.jp/seiga/im6012363",
        "http://seiga.nicovideo.jp/seiga/im4087382#_=_": "https://seiga.nicovideo.jp/seiga/im4087382",

        "https://nico.ms/im10922621": "https://seiga.nicovideo.jp/seiga/im10922621",
    },
    ns.NicoSeigaMangaUrl: {
        "https://seiga.nicovideo.jp/watch/mg316708": "https://seiga.nicovideo.jp/watch/mg316708",
        "https://sp.seiga.nicovideo.jp/watch/mg316708": "https://seiga.nicovideo.jp/watch/mg316708",

        "https://nico.ms/mg310193": "https://seiga.nicovideo.jp/watch/mg310193",
    },
    ns.NicoSeigaArtistUrl: {
        "https://seiga.nicovideo.jp/user/illust/456831": "https://seiga.nicovideo.jp/user/illust/456831",
        "https://sp.seiga.nicovideo.jp/user/illust/20542122": "https://seiga.nicovideo.jp/user/illust/20542122",
        "https://ext.seiga.nicovideo.jp/user/illust/20542122": "https://seiga.nicovideo.jp/user/illust/20542122",
        "http://seiga.nicovideo.jp/manga/list?user_id=23839737": "https://seiga.nicovideo.jp/user/illust/23839737",
        "http://sp.seiga.nicovideo.jp/manga/list?user_id=23839737": "https://seiga.nicovideo.jp/user/illust/23839737",
    },
    ns.NicoSeigaComicUrl: {
        "https://seiga.nicovideo.jp/comic/1571": "https://seiga.nicovideo.jp/comic/1571",
        "http://seiga.nicovideo.jp/manga/rchero": "https://seiga.nicovideo.jp/comic/rchero",
    },
    ns.NicoSeigaImageUrl: {
        "https://seiga.nicovideo.jp/image/source/3521156": "https://seiga.nicovideo.jp/image/source/3521156",
        "https://seiga.nicovideo.jp/image/source/4744553": "https://seiga.nicovideo.jp/image/source/4744553",
        "https://seiga.nicovideo.jp/image/source?id=3521156": "https://seiga.nicovideo.jp/image/source/3521156",
        "https://seiga.nicovideo.jp/image/redirect?id=3583893": "https://seiga.nicovideo.jp/image/source/3583893",

        "https://lohas.nicoseiga.jp/o/971eb8af9bbcde5c2e51d5ef3a2f62d6d9ff5552/1589933964/3583893": "https://seiga.nicovideo.jp/image/source/3583893",

        "https://lohas.nicoseiga.jp/priv/b80f86c0d8591b217e7513a9e175e94e00f3c7a1/1384936074/3583893": "https://seiga.nicovideo.jp/image/source/3583893",
        "https://lohas.nicoseiga.jp/priv/3521156?e=1382558156&h=f2e089256abd1d453a455ec8f317a6c703e2cedf": "https://seiga.nicovideo.jp/image/source/3521156",
        "https://lohas.nicoseiga.jp/thumb/2163478i": "https://seiga.nicovideo.jp/image/source/2163478",
        "https://lohas.nicoseiga.jp/thumb/1591081q": "https://seiga.nicovideo.jp/image/source/1591081",
        "https://lohas.nicoseiga.jp/thumb/4744553p": "https://seiga.nicovideo.jp/image/source/4744553",

        # https://lohas.nicoseiga.jp/material/5746c5/4459092?

        "https://deliver.cdn.nicomanga.jp/thumb/7891081p?1590171867": "https://seiga.nicovideo.jp/image/source/7891081",
        "https://drm.cdn.nicomanga.jp/image/d4a2faa68ec34f95497db6601a4323fde2ccd451_9537/8017978p?1570012695": "https://seiga.nicovideo.jp/image/source/8017978",
        "https://dcdn.cdn.nimg.jp/priv/62a56a7f67d3d3746ae5712db9cac7d465f4a339/1592186183/10466669": "https://seiga.nicovideo.jp/image/source/10466669",
        "https://dcdn.cdn.nimg.jp/nicoseiga/lohas/o/8ba0a9b2ea34e1ef3b5cc50785bd10cd63ec7e4a/1592187477/10466669": "https://seiga.nicovideo.jp/image/source/1046666",

    },
}


generate_parsing_suite(urls)
