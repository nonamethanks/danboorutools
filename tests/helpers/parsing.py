from danboorutools.models.url import Url


def generate_parsing_test(raw_url: str, normalized_url: str | None, expected_class: type[Url]) -> None:
    url = Url.parse(raw_url)

    assert isinstance(url, expected_class)

    if normalized_url:
        actual_normalization = url.normalized_url
        assert actual_normalization == normalized_url
