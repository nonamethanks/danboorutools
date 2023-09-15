from danboorutools.logical.urls import bilibili as b
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    b.BilibiliImageUrl: {
        "https://i0.hdslb.com/bfs/new_dyn/675526fd8baa2f75d7ea0e7ea957bc0811742550.jpg@1036w.webp": "https://i0.hdslb.com/bfs/new_dyn/675526fd8baa2f75d7ea0e7ea957bc0811742550.jpg@1036w.webp",
        "https://i0.hdslb.com/bfs/new_dyn/716a9733fc804d11d823cfacb7a3c78b11742550.jpg@208w_208h_1e_1c.webp": "https://i0.hdslb.com/bfs/new_dyn/716a9733fc804d11d823cfacb7a3c78b11742550.jpg@208w_208h_1e_1c.webp",

        "https://i0.hdslb.com/bfs/album/37f77871d417c76a08a9467527e9670810c4c442.gif@1036w.webp": "https://i0.hdslb.com/bfs/album/37f77871d417c76a08a9467527e9670810c4c442.gif@1036w.webp",
        "https://i0.hdslb.com/bfs/album/37f77871d417c76a08a9467527e9670810c4c442.gif": "https://i0.hdslb.com/bfs/album/37f77871d417c76a08a9467527e9670810c4c442.gif",
        "https://i0.hdslb.com/bfs/article/48e75b3871fa5ed62b4e3a16bf60f52f96b1b3b1.jpg@942w_1334h_progressive.webp": "https://i0.hdslb.com/bfs/article/48e75b3871fa5ed62b4e3a16bf60f52f96b1b3b1.jpg@942w_1334h_progressive.webp",

        # "https://i0.hdslb.com/bfs/activity-plat/static/2cf2b9af5d3c5781d611d6e36f405144/E738vcDvd3.png": None,
        # "http://i1.hdslb.com/bfs/archive/89bfa8427528a5e45eff457d4af3a59a9d3f54e0.jpg": None,
    },
    b.BilibiliPostUrl: {
        "https://m.bilibili.com/dynamic/612214375070704555": "https://t.bilibili.com/612214375070704555",
        "https://www.bilibili.com/opus/684571925561737250": "https://t.bilibili.com/684571925561737250",
        "https://h.bilibili.com/83341894": "https://h.bilibili.com/83341894",


        "https://t.bilibili.com/686082748803186697": "https://t.bilibili.com/686082748803186697",
        "https://t.bilibili.com/723052706467414039?spm_id_from=333.999.0.0": "https://t.bilibili.com/723052706467414039",
        "https://t.bilibili.com/h5/dynamic/detail/410234698927673781": "https://t.bilibili.com/410234698927673781",

        "https://www.bilibili.com/p/h5/8773541": "https://h.bilibili.com/8773541",
    },
    b.BilibiliArticleUrl: {
        "https://www.bilibili.com/read/cv7360489": "https://www.bilibili.com/read/cv7360489",
    },
    b.BilibiliVideoPostUrl: {
        "https://www.bilibili.com/video/BV1dY4y1u7Vi/": "https://www.bilibili.com/video/BV1dY4y1u7Vi",
        "http://www.bilibili.tv/video/av439451/": "https://www.bilibili.com/video/av439451",
    },
    b.BilibiliArtistUrl: {
        "https://space.bilibili.com/355143": "https://space.bilibili.com/355143",
        "https://space.bilibili.com/476725595/dynamic": "https://space.bilibili.com/476725595",
        "https://space.bilibili.com/476725595/video": "https://space.bilibili.com/476725595",
        "http://www.bilibili.tv/member/index.php?mid=66804": "https://space.bilibili.com/66804",
        "https://h.bilibili.com/member?mod=space%5Cu0026uid=4617101%5Cu0026act=p_index": "https://space.bilibili.com/4617101",
        "https://link.bilibili.com/p/world/index#/32122361/world/": "https://space.bilibili.com/32122361",
        "https://m.bilibili.com/space/489905": "https://space.bilibili.com/489905",
        "http://space.bilibili.com/13574506#/album": "https://space.bilibili.com/13574506",
    },
    b.BilibiliLiveUrl: {
        "https://live.bilibili.com/43602": "https://live.bilibili.com/43602",
    },
}


generate_parsing_suite(urls)


assert_artist_url(
    "https://space.bilibili.com/1919593",
    url_type=b.BilibiliArtistUrl,
    url_properties=dict(user_id=1919593),
    primary_names=["嘉露香叶"],
    secondary_names=["bilibili 1919593"],
    related=[],

)
