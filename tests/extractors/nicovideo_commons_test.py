from tests.extractors import generate_parsing_suite
from danboorutools.logical.extractors import nicovideo_commons as nc

urls = {
    nc.NicovideoCommonsArtistUrl: {
        "https://commons.nicovideo.jp/user/696839": "https://commons.nicovideo.jp/user/696839",
    },
    nc.NicovideoCommonsPostUrl: {
        "https://commons.nicovideo.jp/material/nc138051": "https://commons.nicovideo.jp/material/nc138051",
        "https://deliver.commons.nicovideo.jp/thumbnail/nc285306?size=ll": "https://commons.nicovideo.jp/material/nc285306",
    }
}


generate_parsing_suite(urls)
