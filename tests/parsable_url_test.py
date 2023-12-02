import pytest

from danboorutools.logical.parsable_url import ParsableUrl


@pytest.mark.parsing
def test_parameter_parsing() -> None:
    url = "https://www.patreon.com/bePatron?c=170214\u0026rid=218676\u0026redirect_uri=/posts/makoto-nanaya-8366347"
    assert ParsableUrl(url).query == {"c": "170214", "rid": "218676", "redirect_uri": "/posts/makoto-nanaya-8366347"}
