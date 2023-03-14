from danboorutools.logical.extractors.twpf import TwpfUrl
from tests.extractors import generate_parsing_suite

urls = {
    TwpfUrl: {
        "https://twpf.jp/kudan_ruruyie": "https://twpf.jp/kudan_ruruyie",
    },
}


generate_parsing_suite(urls)
