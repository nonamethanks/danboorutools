from danboorutools.logical.urls.sakura import SakuraBlogUrl
from tests.urls import generate_parsing_suite

urls = {
    SakuraBlogUrl: {
        "http://llauda.sakura.ne.jp/": "",
        "https://llauda.sakura.ne.jp/lll/926": "",
        "https://llauda.sakura.ne.jp/lll/files/medias/20210618031521.jpg": "",
        "http://www116.sakura.ne.jp/~kuromoji/": "",
        "http://warden.x0.com": "",
    },

}


generate_parsing_suite(urls)
