from danboorutools.logical.urls.misskey import MisskeyUserUrl
from tests.urls import generate_parsing_suite

urls = {
    MisskeyUserUrl: {
        "https://misskey.io/@snail0326": "https://misskey.io/@snail0326",
    },
}

generate_parsing_suite(urls)
