from ward import test

from danboorutools.logical.parsable_url import ParsableUrl


@test("Parse an url with slashes in the url params", tags=["parsing"])
def parse_param_slashes() -> None:
    url = "https://www.patreon.com/bePatron?c=170214\u0026rid=218676\u0026redirect_uri=/posts/makoto-nanaya-8366347"
    assert ParsableUrl(url).params == {'c': '170214', 'rid': '218676', 'redirect_uri': '/posts/makoto-nanaya-8366347'}
