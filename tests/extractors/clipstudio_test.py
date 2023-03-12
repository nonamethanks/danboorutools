from danboorutools.logical.extractors.clipstudio import (
    ClipStudioAssetPostUrl,
    ClipStudioBlogUrl,
    ClipStudioProfileUrl,
    ClipStudioUserSearchUrl,
)
from tests.extractors import generate_parsing_suite

urls = {
    ClipStudioAssetPostUrl: {
        "https://assets.clip-studio.com/ja-jp/detail?id=1946309": "https://assets.clip-studio.com/en-us/detail?id=1946309",
    },
    ClipStudioProfileUrl: {
        "https://profile.clip-studio.com/ja-jp/profile/cxhgegm-sc": "https://profile.clip-studio.com/en-us/profile/cxhgegm-sc",
        "https://profile.clip-studio.com/en-us/profile/gch9jit-cw": "https://profile.clip-studio.com/en-us/profile/gch9jit-cw",
    },
    ClipStudioUserSearchUrl: {
        "https://assets.clip-studio.com/ja-jp/search?user=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8F&order=new": "https://assets.clip-studio.com/en-us/search?user=隼人ろっく",
    },
    ClipStudioBlogUrl: {
        "http://fuujin.sees.clip-studio.com/": "http://fuujin.sees.clip-studio.com/site/",
        "http://fuujin.sees.clip-studio.com/site/": "http://fuujin.sees.clip-studio.com/site/",
    },
}


generate_parsing_suite(urls)
