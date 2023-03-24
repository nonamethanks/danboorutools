from danboorutools.logical.urls.hatena import (
    HatenaBlogPostUrl,
    HatenaBlogUrl,
    HatenaFotolifeArtistUrl,
    HatenaFotolifePostUrl,
    HatenaProfileUrl,
    HatenaUgomemoUrl,
)
from tests.urls import assert_artist_url, assert_info_url, generate_parsing_suite

urls = {
    HatenaFotolifeArtistUrl: {
        "http://f.hatena.ne.jp/msmt1118/": "https://f.hatena.ne.jp/msmt1118/",
        "http://img.f.hatena.ne.jp/images/fotolife/m/mauuuuuu/": "https://f.hatena.ne.jp/mauuuuuu/",
        "http://f.hatena.ne.jp/images/fotolife/b/beni/20100403/": "https://f.hatena.ne.jp/beni/",
        "http://f.hatena.ne.jp/kazeshima/風島１８/": "https://f.hatena.ne.jp/kazeshima/",
    },
    HatenaFotolifePostUrl: {
        "https://f.hatena.ne.jp/msmt1118/20190927210959": "https://f.hatena.ne.jp/msmt1118/20190927210959",
    },
    HatenaUgomemoUrl: {
        "http://ugomemo.hatena.ne.jp/167427A0CEF89DA2@DSi/": "https://ugomemo.hatena.ne.jp/167427A0CEF89DA2@DSi/",
    },
    HatenaProfileUrl: {
        "https://profile.hatena.ne.jp/gekkakou616/": "https://profile.hatena.ne.jp/gekkakou616/",
        "http://www.hatena.ne.jp/ranpha/": "https://profile.hatena.ne.jp/ranpha/",
        "http://kokage.g.hatena.ne.jp/kokage/": "https://profile.hatena.ne.jp/kokage/",
        "http://h.hatena.ne.jp/jandare-210/": "https://profile.hatena.ne.jp/jandare-210/",
        "http://h.hatena.ne.jp/id/rera": "https://profile.hatena.ne.jp/rera/",
        "http://b.hatena.ne.jp/kat_cloudair/": "https://profile.hatena.ne.jp/kat_cloudair/",
        "https://profile.hatena.ne.jp/Lukecarter/profile": "https://profile.hatena.ne.jp/Lukecarter/",
        "https://q.hatena.ne.jp/ten59": "https://profile.hatena.ne.jp/ten59/",
    },
    HatenaBlogUrl: {
        "http://blog.hatena.ne.jp/daftomiken/": "https://daftomiken.hatenablog.com",
        "http://daftomiken.hatenablog.com": "https://daftomiken.hatenablog.com",
        "http://satsukiyasan.hatenablog.com/about": "https://satsukiyasan.hatenablog.com",

        "https://ten59.hatenadiary.org": "https://ten59.hatenadiary.org",
        "http://d.hatena.ne.jp/ten59/": "https://ten59.hatenadiary.org",
        "https://blog.hatena.ne.jp/login?blog=https%3A%2F%2Fam-1-00.hatenadiary.org%2F": "https://am-1-00.hatenadiary.org",
        "http://d.hatena.ne.jp/images/diary/t/taireru/": "https://taireru.hatenadiary.org",
        "http://d.hatena.ne.jp/kab_studio/searchdiary?word=%2a%5b%b3%a8%5d": "https://kab-studio.hatenadiary.org",
        "http://d.hatena.ne.jp/votamochi/20091015": "https://votamochi.hatenadiary.org",
        "https://votamochi.hatenadiary.org/entries/2009/10/15": "https://votamochi.hatenadiary.org",
    },
    HatenaBlogPostUrl: {
        "https://fujikino.hatenablog.com/entry/2018/01/27/041829": "https://fujikino.hatenablog.com/entry/2018/01/27/041829",

        "http://d.hatena.ne.jp/gentoji/00000204/1282974942": "https://gentoji.hatenadiary.org/entry/00000204/1282974942",
    },
}


generate_parsing_suite(urls)


assert_info_url(
    "https://profile.hatena.ne.jp/gekkakou616/",
    HatenaProfileUrl,
    url_properties=dict(username="gekkakou616"),
    primary_names=["りゅーがもの"],
    secondary_names=["gekkakou616"],
    related=["http://pixiv.me/gmk616"],
)


assert_artist_url(
    "https://f.hatena.ne.jp/msmt1118/",
    HatenaFotolifeArtistUrl,
    url_properties=dict(username="msmt1118"),
    primary_names=[],
    secondary_names=["msmt1118"],
    related=["https://profile.hatena.ne.jp/msmt1118/"],
)
