from danboorutools.logical.extractors import fanza as fz
from tests.extractors import assert_post_url, generate_parsing_suite

urls = {
    fz.FanzaDoujinAuthorUrl: {
        "https://www.dmm.co.jp/dc/doujin/-/list/=/article=maker/id=70980": "https://www.dmm.co.jp/dc/doujin/-/list/=/article=maker/id=70980/",
        "http://www.dmm.co.jp/digital/doujin/-/list/=/article=maker/id=27726/": "https://www.dmm.co.jp/digital/doujin/-/list/=/article=maker/id=27726/",
        "http://www.dmm.co.jp/mono/doujin/-/list/=/article=maker/id=20225/": "https://www.dmm.co.jp/mono/doujin/-/list/=/article=maker/id=20225/",
        "http://www.dmm.co.jp/digital/doujin/-/list/=/article=maker/id=26019/sort=date": "https://www.dmm.co.jp/digital/doujin/-/list/=/article=maker/id=26019/",
        "http://www.dmm.co.jp/en/dc/doujin/-/list/=/article=maker/id=29820/": "https://www.dmm.co.jp/dc/doujin/-/list/=/article=maker/id=29820/"
    },
    fz.FanzaDoujinWorkUrl: {
        "https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_218503%2F&af_id=conoco-002": "https://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_218503/",
        "https://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_cs0949/": "https://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_cs0949/",
    },
    fz.FanzaDlsoftWorkUrl: {
        "https://dlsoft.dmm.co.jp/detail/jveilelwy_0001/": "https://dlsoft.dmm.co.jp/detail/jveilelwy_0001/",
        "http://www.dmm.co.jp/digital/pcgame/-/detail/=/cid=tech_0003/": "https://dlsoft.dmm.co.jp/detail/tech_0003/",
    },
    fz.FanzaDlsoftAuthorUrl: {
        "https://dlsoft.dmm.co.jp/list/article=maker/id=30267/": "https://dlsoft.dmm.co.jp/list/article=maker/id=30267/",
        "http://dlsoft.dmm.co.jp/list/article=author/id=239811/": "https://dlsoft.dmm.co.jp/list/article=author/id=239811/"
    },
    fz.FanzaBookAuthorUrl: {
        "https://book.dmm.co.jp/list/?author=254530": "https://book.dmm.co.jp/list/?author=254530",
        "http://www.dmm.co.jp/dc/book/-/list/=/article=author/id=254530/media=comic": "https://book.dmm.co.jp/list/?author=254530",
        "http://www.dmm.co.jp/digital/book/-/list/=/article=author/id=240536/media=comic/": "https://book.dmm.co.jp/list/?author=240536",
        "http://book.dmm.co.jp/list/comic/?floor=Abook\u0026article=author\u0026id=257051\u0026type=single": "https://book.dmm.co.jp/list/?author=257051",
        "http://book.dmm.co.jp/author/256941/": "https://book.dmm.co.jp/list/?author=256941",
        "http://book.dmm.co.jp/list/comic/?floor=Abook\u0026article=author\u0026id=25105/": "https://book.dmm.co.jp/list/?author=25105",
        "https://book.dmm.co.jp/author/238380/OBBM-001": "https://book.dmm.co.jp/list/?author=238380",
        "https://www.dmm.co.jp/mono/book/-/list/=/article=author/id=240684/": "https://book.dmm.co.jp/list/?author=240684",
    },
    fz.FanzaBookWorkUrl: {
        "https://book.dmm.co.jp/product/761338/b472abnen00334/": "https://book.dmm.co.jp/product/761338/b472abnen00334/",
        "https://www.dmm.co.jp/mono/book/-/detail/=/cid=204book18118122016/": "https://www.dmm.co.jp/mono/book/-/detail/=/cid=204book18118122016/",
    },
    fz.FanzaBookNoSeriesUrl: {
        "http://book.dmm.co.jp/detail/b915awnmg00690/": "https://book.dmm.co.jp/detail/b915awnmg00690/",
        "http://www.dmm.co.jp/dc/book/-/detail/=/cid=b073bktcm00445": "https://book.dmm.co.jp/detail/b073bktcm00445/",
        "http://book.dmm.co.jp/detail/b061bangl00828/ozy3jyayo-001": "https://book.dmm.co.jp/detail/b061bangl00828/"
    },
    fz.FanzaGamesGameUrl: {
        "https://games.dmm.co.jp/detail/devilcarnival": "https://games.dmm.co.jp/detail/devilcarnival",
        "http://www.dmm.co.jp/netgame_s/flower-x": "https://games.dmm.co.jp/detail/flower-x",
    },
    fz.FanzaGamesOldGameUrl: {
        "http://sp.dmm.co.jp/netgame/application/detail/app_id/968828": "http://sp.dmm.co.jp/netgame/application/detail/app_id/968828",
    },
    fz.FanzaImageUrl: {
        "https://doujin-assets.dmm.co.jp/digital/comic/d_261113/d_261113jp-001.jpg": "https://doujin-assets.dmm.co.jp/digital/comic/d_261113/d_261113jp-001.jpg",
        "https://doujin-assets.dmm.co.jp/digital/comic/d_261113/d_261113pl.jpg": "https://doujin-assets.dmm.co.jp/digital/comic/d_261113/d_261113pl.jpg",
        "https://doujin-assets.dmm.co.jp/digital/comic/d_218503/d_218503pr.jpg": "https://doujin-assets.dmm.co.jp/digital/comic/d_218503/d_218503pl.jpg",
        "https://pics.dmm.co.jp/mono/comic/420abgoods022/420abgoods022pl.jpg": "https://pics.dmm.co.jp/mono/comic/420abgoods022/420abgoods022pl.jpg",
        "https://pics.dmm.co.jp/mono/doujin/d_d0014920/d_d0014920jp-002.jpg": "https://pics.dmm.co.jp/mono/doujin/d_d0014920/d_d0014920jp-002.jpg",

        "https://pics.dmm.co.jp/digital/pcgame/jveilelwy_0001/jveilelwy_0001jp-001.jpg": "https://pics.dmm.co.jp/digital/pcgame/jveilelwy_0001/jveilelwy_0001jp-001.jpg",
        "https://pics.dmm.co.jp/digital/pcgame/jveilelwy_0001/jveilelwy_0001pl.jpg": "https://pics.dmm.co.jp/digital/pcgame/jveilelwy_0001/jveilelwy_0001pl.jpg",

        "http://p.dmm.co.jp/p/netgame/feature/gemini/cp_02_chara_01.png": "http://p.dmm.co.jp/p/netgame/feature/gemini/cp_02_chara_01.png",

        "https://pics.dmm.co.jp/mono/goods/ho5761/ho5761jp-007.jpg": "https://pics.dmm.co.jp/mono/goods/ho5761/ho5761jp-007.jpg",

        "http://pics.dmm.co.jp/digital/video/66nov08380/66nov08380pl.jpg": "https://pics.dmm.co.jp/digital/video/66nov08380/66nov08380pl.jpg",

        "http://pics.dmm.co.jp/mono/game/1927apc10857/1927apc10857pl.jpg": "https://pics.dmm.co.jp/mono/game/1927apc10857/1927apc10857pl.jpg",
    },
}


generate_parsing_suite(urls)

assert_post_url(
    "https://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_218503/",
    url_type=fz.FanzaDoujinWorkUrl,
    url_properties=dict(work_id="d_218503", subsubsite="dc"),
    gallery="https://www.dmm.co.jp/dc/doujin/-/list/=/article=maker/id=70980/",
)

assert_post_url(
    "https://book.dmm.co.jp/product/4102975/b064bcmcm01996/?utm_medium=dmm_affiliate&utm_source=conoco-990&utm_campaign=affiliate_api",
    url_type=fz.FanzaBookWorkUrl,
    url_properties=dict(series_id=4102975, work_id="b064bcmcm01996"),
    gallery="https://book.dmm.co.jp/list/?author=238988",
)
