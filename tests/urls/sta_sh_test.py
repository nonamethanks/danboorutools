import pytest

from danboorutools.logical.urls.stash import StaShUrl
from tests.helpers.parsing import generate_parsing_test

urls = {
    StaShUrl: {
        "https://sta.sh/21leo8mz87ue": "https://sta.sh/21leo8mz87ue",
        "https://sta.sh/2uk0v5wabdt": "https://sta.sh/2uk0v5wabdt",
        "https://sta.sh/0wxs31o7nn2": "https://sta.sh/0wxs31o7nn2",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
