from danboorutools.logical.extractors.misskey import MisskeyUserUrl
from tests.extractors import generate_parsing_suite

urls = {
    MisskeyUserUrl: {
        "https://misskey.io/@snail0326": "https://misskey.io/@snail0326",
    },
}

generate_parsing_suite(urls)
