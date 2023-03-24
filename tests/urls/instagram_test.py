from danboorutools.logical.urls.instagram import InstagramArtistUrl, InstagramPostUrl
from tests.urls import generate_parsing_suite

urls = {
    InstagramArtistUrl: {
        "https://www.instagram.com/itomugi/": "https://www.instagram.com/itomugi",
        "https://www.instagram.com/itomugi/tagged/": "https://www.instagram.com/itomugi",
        "https://www.instagram.com/stories/itomugi/": "https://www.instagram.com/itomugi",
    },
    InstagramPostUrl: {
        "https://www.instagram.com/p/CbDW9mVuEnn/": "https://www.instagram.com/p/CbDW9mVuEnn",
        "https://www.instagram.com/reel/CV7mHEwgbeF/?utm_medium=copy_link": "https://www.instagram.com/p/CV7mHEwgbeF",
        "https://www.instagram.com/tv/CMjUD1epVWW/": "https://www.instagram.com/p/CMjUD1epVWW",
    },
}

generate_parsing_suite(urls)
