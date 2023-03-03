from danboorutools.logical.extractors.sakura import SakuraBlogUrl
from tests.extractors import generate_parsing_suite

urls = {
    SakuraBlogUrl: {
        "http://llauda.sakura.ne.jp/": "",
        "https://llauda.sakura.ne.jp/lll/926": "",
        "https://llauda.sakura.ne.jp/lll/files/medias/20210618031521.jpg": "",
        "http://www116.sakura.ne.jp/~kuromoji/": "",
    },

}


generate_parsing_suite(urls)
