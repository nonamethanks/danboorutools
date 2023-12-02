import pytest

from danboorutools.logical.urls import fc2
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    fc2.Fc2BlogUrl: {
        "http://silencexs.blog.fc2.com": "http://silencexs.blog.fc2.com",
        "http://silencexs.blog106.fc2.com": "http://silencexs.blog.fc2.com",
        "http://chika108.blog.2nt.com": "http://chika108.blog.2nt.com",

        "http://794ancientkyoto.web.fc2.com": "http://794ancientkyoto.web.fc2.com",
        "http://yorokobi.x.fc2.com": "http://yorokobi.x.fc2.com",
        "https://lilish28.bbs.fc2.com": "http://lilish28.bbs.fc2.com",
        "http://jpmaid.h.fc2.com": "http://jpmaid.h.fc2.com",


        "http://toritokaizoku.web.fc2.com/tori.html": "http://toritokaizoku.web.fc2.com",

        "http://swordsouls.blog131.fc2blog.net": "http://swordsouls.blog.fc2blog.net",
        "http://swordsouls.blog131.fc2blog.us": "http://swordsouls.blog.fc2blog.us",


        "http://ojimahonpo.web.fc2.com/site/": "http://ojimahonpo.web.fc2.com",
        "http://ramepan.web.fc2.com/pict/": "http://ramepan.web.fc2.com",
        "http://celis.x.fc2.com/gallery/dai3_2/dai3_2.htm": "http://celis.x.fc2.com",
        "http://seimen10.h.fc2.com/top.htm": "http://seimen10.h.fc2.com",

        "http://blog-imgs-32.fc2.com/e/r/o/erosanimest/": "http://erosanimest.blog.fc2.com",
        "https://usagigoyakikaku.cart.fc2.com/?preview=31plzD8O7SP3": "http://usagigoyakikaku.cart.fc2.com",

        "http://blog36.fc2.com/acidhead": "http://acidhead.blog.fc2.com",

        "http://tororohanrok.blog111.fc2.com/category7-1": "http://tororohanrok.blog.fc2.com",

        "http://blog.fc2.com/m/mosha2/": "http://mosha2.blog.fc2.com",

    },
    fc2.Fc2ImageUrl: {

        "http://onidocoro.blog14.fc2.com/file/20071003061150.png": "http://onidocoro.blog14.fc2.com/file/20071003061150.png",
        "http://blog23.fc2.com/m/mosha2/file/uru.jpg": "http://blog23.fc2.com/m/mosha2/file/uru.jpg",
        "http://blog.fc2.com/g/genshi/file/20070612a.jpg": "http://blog.fc2.com/g/genshi/file/20070612a.jpg",

        "http://blog-imgs-63-origin.fc2.com/y/u/u/yuukyuukikansya/140817hijiri02.jpg": "http://blog-imgs-63-origin.fc2.com/y/u/u/yuukyuukikansya/140817hijiri02.jpg",
        "http://blog-imgs-61.fc2.com/o/m/o/omochi6262/20130402080220583.jpg": "http://blog-imgs-61.fc2.com/o/m/o/omochi6262/20130402080220583.jpg",
        "http://blog.fc2.com/g/b/o/gbot/20071023195141.jpg": "http://blog.fc2.com/g/b/o/gbot/20071023195141.jpg",


        "http://diary.fc2.com/user/yuuri/img/2005_12/26.jpg": "http://diary.fc2.com/user/yuuri/img/2005_12/26.jpg",
        "http://diary1.fc2.com/user/kou_48/img/2006_8/14.jpg": "http://diary1.fc2.com/user/kou_48/img/2006_8/14.jpg",
        "http://diary.fc2.com/user/kazuharoom/img/2015_5/22.jpg": "http://diary.fc2.com/user/kazuharoom/img/2015_5/22.jpg",
        "http://doskoinpo.blog133.fc2.com/?mode=image&filename=SIBARI03.jpg": "http://doskoinpo.blog133.fc2.com/?mode=image&filename=SIBARI03.jpg",
        "http://doskoinpo.blog133.fc2.com/img/SIBARI03.jpg/": "http://doskoinpo.blog133.fc2.com/img/SIBARI03.jpg/",
        "https://blog-imgs-19.fc2.com/5/v//5v/yukkuri0.jpg": "https://blog-imgs-19.fc2.com/5/v//5v/yukkuri0.jpg",
        "http://shohomuga.blog83.fc2.com/20071014181747.jpg": "http://shohomuga.blog83.fc2.com/20071014181747.jpg",
        "https://blog-imgs-145-origin.2nt.com/k/a/t/katourennyuu/210626_0003.jpg": "https://blog-imgs-145-origin.2nt.com/k/a/t/katourennyuu/210626_0003.jpg",

    },
    fc2.Fc2PostUrl: {
        "http://hosystem.blog36.fc2.com/blog-entry-37.html": "http://hosystem.blog.fc2.com/blog-entry-37.html",
        "http://kozueakari02.blog.2nt.com/blog-entry-115.html": "http://kozueakari02.blog.2nt.com/blog-entry-115.html",
    },
    fc2.Fc2PiyoPostUrl: {
        "https://piyo.fc2.com/omusubi/26890/": "https://piyo.fc2.com/omusubi/26890",
    },
    fc2.Fc2PiyoBlogUrl: {
        "https://piyo.fc2.com/omusubi": "https://piyo.fc2.com/omusubi",
        "https://piyo.fc2.com/omusubi/start/5/": "https://piyo.fc2.com/omusubi",
    },
    fc2.Fc2DiaryPostUrl: {
        "http://diary.fc2.com/cgi-sys/ed.cgi/kazuharoom/?Y=2012&M=10&D=22": "http://diary.fc2.com/cgi-sys/ed.cgi/kazuharoom/?Y=2012&M=10&D=22",
    },
    fc2.Fc2DiaryArtistUrl: {
        "http://diary.fc2.com/cgi-sys/ed.cgi/kazuharoom/": "http://diary.fc2.com/cgi-sys/ed.cgi/kazuharoom",

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
        url_string="http://mogu08.blog104.fc2.com/",
        url_type=fc2.Fc2BlogUrl,
        url_properties=dict(username="mogu08", domain="fc2.com", subsite="blog"),
        related=[],
        primary_names=["あきらめmo。"],
        secondary_names=["mogu08"],
    )


def test_artist_url_2():
    generate_artist_test(
        url_string="http://laindell.blog.2nt.com/",
        url_type=fc2.Fc2BlogUrl,
        url_properties=dict(username="laindell", domain="2nt.com", subsite="blog"),
        related=[],
        primary_names=["れいんでる"],
        secondary_names=["laindell"],
    )


def test_artist_url_3():
    generate_artist_test(
        url_string="http://kudanya.blog42.fc2.com/",
        url_type=fc2.Fc2BlogUrl,
        url_properties=dict(username="kudanya", domain="fc2.com", subsite="blog"),
        related=[],
        primary_names=["くだんや"],
        secondary_names=["kudanya"],
    )


def test_artist_url_4():
    generate_artist_test(
        url_string="http://cocy.blog57.fc2.com/",
        url_type=fc2.Fc2BlogUrl,
        url_properties=dict(username="cocy", domain="fc2.com", subsite="blog"),
        related=[],
        primary_names=["寝起きふう"],
        secondary_names=["cocy"],
    )


def test_artist_url_5():
    generate_artist_test(
        url_string="http://xxxmixberry.web.fc2.com/",
        url_type=fc2.Fc2BlogUrl,
        url_properties=dict(username="xxxmixberry", domain="fc2.com", subsite="web"),
        related=[],
        primary_names=["millefeuille"],
        secondary_names=["xxxmixberry"],
    )
