from danboorutools.logical.extractors.clipstudio import ClipStudioAssetPostUrl, ClipStudioProfileUrl, ClipStudioUserSearchUrl
from tests.extractors import generate_parsing_suite

urls = {
    ClipStudioAssetPostUrl: {
        "https://assets.clip-studio.com/ja-jp/detail?id=1946309": "https://assets.clip-studio.com/ja-jp/detail?id=1946309",
    },
    ClipStudioProfileUrl: {
        "https://profile.clip-studio.com/ja-jp/profile/cxhgegm-sc": "https://profile.clip-studio.com/ja-jp/profile/cxhgegm-sc",
    },
    ClipStudioUserSearchUrl: {
        "https://assets.clip-studio.com/ja-jp/search?user=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8F&order=new": "https://assets.clip-studio.com/ja-jp/search?user=隼人ろっく",
    },
}


generate_parsing_suite(urls)
