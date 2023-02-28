from ward import test

from danboorutools.models.url import Url

urls = {
    "https://comic.pixiv.net/viewer/stories/107927": "https://comic.pixiv.net/viewer/stories/107927",
    "https://comic.pixiv.net/works/8683": "https://comic.pixiv.net/works/8683",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
