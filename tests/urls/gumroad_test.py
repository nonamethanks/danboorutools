from danboorutools.logical.urls.gumroad import GumroadArtistUrl, GumroadImageUrl, GumroadPostNoArtist, GumroadPostUrl
from tests.urls import generate_parsing_suite

urls = {
    GumroadArtistUrl: {
        "https://roborobocap.gumroad.com/": "https://roborobocap.gumroad.com",
        "https://app.gumroad.com/roborobocap": "https://roborobocap.gumroad.com",
    },
    GumroadPostUrl: {
        "https://fishsyrup.gumroad.com/l/WkjEj/ibdkpxx": "https://fishsyrup.gumroad.com/l/WkjEj",
        "https://fishsyrup.gumroad.com/l/WkjEj": "https://fishsyrup.gumroad.com/l/WkjEj",
    },
    GumroadPostNoArtist: {
        "http://gumroad.com/l/uSukO/": "https://app.gumroad.com/l/uSukO",
        "https://gumroad.com/l/WkjEj/ibdkpxx": "https://app.gumroad.com/l/WkjEj",
    },
    GumroadImageUrl: {
        "https://public-files.gumroad.com/zly28g1k8xyhvrzcm0ngs596jb1d": "",
        "https://public-files.gumroad.com/variants/nyciujfjsdcfh6vj9j5om56lve7z/e82ce07851bf15f5ab0ebde47958bb042197dbcdcae02aa122ef3f5b41e97c02": "",
        "https://static-2.gumroad.com/res/gumroad/6148433509922/asset_previews/7e296db4cc949bb42eb2ac73b6b92f42/retina/samus_dada_normal.jpg": "",
    },
}


generate_parsing_suite(urls)
