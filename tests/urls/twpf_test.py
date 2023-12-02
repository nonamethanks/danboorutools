import pytest

from danboorutools.logical.urls.twpf import TwpfUrl
from tests.helpers.parsing import generate_parsing_test

urls = {
    TwpfUrl: {
        "https://twpf.jp/kudan_ruruyie": "https://twpf.jp/kudan_ruruyie",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
