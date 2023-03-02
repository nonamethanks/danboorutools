from danboorutools.logical.extractors.anifty import AniftyArtistUrl, AniftyPostUrl, AniftyTokenUrl
from tests.extractors import generate_parsing_suite

urls = {
    AniftyPostUrl: {
        "https://anifty.jp/creations/373": "https://anifty.jp/creations/373",
        "https://anifty.jp/ja/creations/373": "https://anifty.jp/creations/373",
        "https://anifty.jp/zh/creations/373": "https://anifty.jp/creations/373",
        "https://anifty.jp/zh-Hant/creations/373": "https://anifty.jp/creations/373",
    },
    AniftyArtistUrl: {
        "https://anifty.jp/@hightree": "https://anifty.jp/@hightree",
        "https://anifty.jp/ja/@hightree": "https://anifty.jp/@hightree",
    },
    AniftyTokenUrl: {
        "https://anifty.jp/tokens/17": "https://anifty.jp/tokens/17",
    }
}


generate_parsing_suite(urls)
