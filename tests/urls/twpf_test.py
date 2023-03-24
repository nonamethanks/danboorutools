from danboorutools.logical.urls.twpf import TwpfUrl
from tests.urls import generate_parsing_suite

urls = {
    TwpfUrl: {
        "https://twpf.jp/kudan_ruruyie": "https://twpf.jp/kudan_ruruyie",
    },
}


generate_parsing_suite(urls)
