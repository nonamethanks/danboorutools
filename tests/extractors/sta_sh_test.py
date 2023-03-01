from ward import test

from danboorutools.models.url import Url

urls = {
    "https://sta.sh/21leo8mz87ue": "https://sta.sh/21leo8mz87ue",
    "https://sta.sh/2uk0v5wabdt": "https://sta.sh/2uk0v5wabdt",
    "https://sta.sh/0wxs31o7nn2": "https://sta.sh/0wxs31o7nn2",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
