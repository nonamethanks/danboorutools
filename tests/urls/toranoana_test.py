from danboorutools.logical.urls.toranoana import (
    ToranoanaArtistUrl,
    ToranoanaCircleUrl,
    ToranoanaDojinSeriesUrl,
    ToranoanaImageUrl,
    ToranoanaItemUrl,
    ToranoanaOldAuthorUrl,
    ToranoanaOldCircleUrl,
    ToranoanaWebcomicPageUrl,
)
from tests.urls import assert_artist_url, assert_post_url, generate_parsing_suite

urls = {
    ToranoanaItemUrl: {
        "http://www.toranoana.jp/mailorder/article/04/0030/82/37/040030823758.html": "https://ec.toranoana.jp/tora_r/ec/item/040030823758/",
        "http://www.toranoana.jp/bl/article/04/0030/51/17/040030511769.html": "https://ec.toranoana.jp/joshi_r/ec/item/040030511769/",
        "https://ec.toranoana.jp/tora_r/ec/item/040030865238/": "https://ec.toranoana.jp/tora_r/ec/item/040030865238/",
    },
    ToranoanaOldAuthorUrl: {
        "http://www.toranoana.jp/mailorder/cot/author/95/3675_01.html": "http://www.toranoana.jp/mailorder/cot/author/95/3675_01.html",
        "http://www.toranoana.jp/bl/cot/author/14/a4a8a4b0_01.html": "http://www.toranoana.jp/bl/cot/author/14/a4a8a4b0_01.html",
    },
    ToranoanaOldCircleUrl: {
        "http://www.toranoana.jp/mailorder/cot/circle/81/02/5730303330323831/b4c5b2c6a5c9a5eda5c3a5d7_01.html": "http://www.toranoana.jp/mailorder/cot/circle/81/02/5730303330323831/b4c5b2c6a5c9a5eda5c3a5d7_01.html",
        "http://dl.toranoana.jp/cgi-bin/coterie_item_search.cgi?circle=00004202270200000001": "http://dl.toranoana.jp/cgi-bin/coterie_item_search.cgi?circle=00004202270200000001",
        "http://www.toranoana.jp/mailorder/ebk/circle/32/93/5730353439333332/cbf5c3e3a5c9a1bca5eb_01.html": "http://www.toranoana.jp/mailorder/ebk/circle/32/93/5730353439333332/cbf5c3e3a5c9a1bca5eb_01.html",
        "http://www.toranoana.jp/bl/cot/circle/18/63/5730303836333138/416c79646572_01.html": "http://www.toranoana.jp/bl/cot/circle/18/63/5730303836333138/416c79646572_01.html",
    },
    ToranoanaDojinSeriesUrl: {
        "http://www.toranoana.jp/info/dojin/120810_oyakokodon": "http://www.toranoana.jp/info/dojin/120810_oyakokodon/",
    },
    ToranoanaCircleUrl: {
        "https://ec.toranoana.jp/tora_r/ec/cot/circle/2UPA346P8473d46Pd687/all/": "https://ec.toranoana.jp/tora_r/ec/cot/circle/2UPA346P8473d46Pd687/all/",
        "https://ecs.toranoana.jp/tora/ec/cot/circle/LUPAdB6Q8U75d06pd687/all/": "https://ecs.toranoana.jp/tora/ec/cot/circle/LUPAdB6Q8U75d06pd687/all/",
        "https://ec.toranoana.jp/joshi_r/ec/cot/circle/2UPA1C6P8X7LdE6Rd687/all/": "https://ec.toranoana.jp/joshi_r/ec/cot/circle/2UPA1C6P8X7LdE6Rd687/all/",
    },
    ToranoanaArtistUrl: {
        "https://ec.toranoana.jp/joshi_r/ec/app/catalog/list?actorKindId=作家★☆★ACTR000002008202": "https://ec.toranoana.jp/joshi_r/ec/app/catalog/list?actorKindId=作家★☆★ACTR000002008202",
        "https://ec.toranoana.jp/tora_r/ec/app/catalog/list?searchActorName=%E4%B8%B8%E6%96%B0": "https://ec.toranoana.jp/tora_r/ec/app/catalog/list?searchActorName=丸新",
    },
    ToranoanaImageUrl: {
        "https://ecdnimg.toranoana.jp/ec/img/04/0030/80/38/040030803886-1p_thumb.jpg": "https://ecdnimg.toranoana.jp/ec/img/04/0030/80/38/040030803886-1p.jpg",
        "https://ecdnimg.toranoana.jp/ec/img/04/0030/80/38/040030803886-1p.jpg": "https://ecdnimg.toranoana.jp/ec/img/04/0030/80/38/040030803886-1p.jpg",
    },
    ToranoanaWebcomicPageUrl: {
        "http://www.toranoana.jp/webcomic/holic/esora/webcomic/hebe/0003/10.jpg": "http://www.toranoana.jp/webcomic/holic/esora/webcomic/hebe/0003/10.html",
        "https://www.toranoana.jp/webcomic/holic/esora/webcomic/kitune/0001/tobira.jpg": "https://www.toranoana.jp/webcomic/holic/esora/webcomic/kitune/0001/01.html",
        "https://www.toranoana.jp/webcomic/holic/esora/webcomic/4koma/karaage/0001/02.html": "https://www.toranoana.jp/webcomic/holic/esora/webcomic/4koma/karaage/0001/02.html",
    },
}


generate_parsing_suite(urls)


assert_post_url(
    "https://ec.toranoana.jp/tora_r/ec/item/040030823758/",
    url_type=ToranoanaItemUrl,
    url_properties=dict(item_id="040030823758", subdirs="tora_r/ec", subsite="ec"),
    gallery="https://ec.toranoana.jp/tora_r/ec/app/catalog/list?searchActorName=mignon",
)

assert_artist_url(
    "https://ec.toranoana.jp/joshi_r/ec/cot/circle/2UPADB6Q8673dA6Td687/all/",
    url_properties=dict(subsite="ec", subdirs="joshi_r/ec/cot", circle_id="2UPADB6Q8673dA6Td687"),
    url_type=ToranoanaCircleUrl,
    primary_names=[],
    secondary_names=["ぎゃくさんかく"],
    related=[],
)
