from danboorutools.models.url import ArtistUrl, Url


def assert_parsed(string: str, url_type: type[Url]) -> None:
    assert isinstance(parsed_type := Url.parse(string), url_type), parsed_type
