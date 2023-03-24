from danboorutools.logical.urls.gamer_tw import GamerTwArtistUrl, GamerTwForumPostUrl, GamerTwGnnPostUrl, GamerTwPostUrl
from tests.urls import generate_parsing_suite

urls = {
    GamerTwArtistUrl: {
        "https://home.gamer.com.tw/homeindex.php?owner=her682913": "https://home.gamer.com.tw/homeindex.php?owner=her682913",
        "http://home.gamer.com.tw/home.php?owner=ader0fabill": "https://home.gamer.com.tw/homeindex.php?owner=ader0fabill",
        "http://home.gamer.com.tw/o0asskiler0o": "https://home.gamer.com.tw/homeindex.php?owner=o0asskiler0o",
        "https://home.gamer.com.tw/creation.php?owner=lcomicer": "https://home.gamer.com.tw/homeindex.php?owner=lcomicer",
    },
    GamerTwPostUrl: {
        "https://home.gamer.com.tw/creationDetail.php?sn=2824881": "https://home.gamer.com.tw/creationDetail.php?sn=2824881",
        "https://home.gamer.com.tw/artwork.php?sn=5245406": "https://home.gamer.com.tw/creationDetail.php?sn=5245406",
    },
    GamerTwForumPostUrl: {
        "https://forum.gamer.com.tw/C.php?page=8\u0026bsn=36399\u0026snA=54": "https://forum.gamer.com.tw/C.php?bsn=36399&snA=54",
        "https://forum.gamer.com.tw/C.php?bsn=7650&snA=1024581": "https://forum.gamer.com.tw/C.php?bsn=7650&snA=1024581",
        "https://forum.gamer.com.tw/Co.php?bsn=31483\u0026sn=2108": "https://forum.gamer.com.tw/Co.php?bsn=31483&sn=2108",
        "https://m.gamer.com.tw/forum/C.php?bsn=34173\u0026snA=5731": "https://forum.gamer.com.tw/C.php?bsn=34173&snA=5731",
    },
    GamerTwGnnPostUrl: {
        "https://gnn.gamer.com.tw/detail.php?sn=190824": "https://gnn.gamer.com.tw/detail.php?sn=190824",
    },
}


generate_parsing_suite(urls)
