
from ward import test

from danboorutools.models.url import Url

urls = {
    "https://www.instagram.com/itomugi/": "https://www.instagram.com/itomugi",
    "https://www.instagram.com/itomugi/tagged/": "https://www.instagram.com/itomugi",
    "https://www.instagram.com/stories/itomugi/": "https://www.instagram.com/itomugi",

    "https://www.instagram.com/p/CbDW9mVuEnn/": "https://www.instagram.com/p/CbDW9mVuEnn",
    "https://www.instagram.com/reel/CV7mHEwgbeF/?utm_medium=copy_link": "https://www.instagram.com/p/CV7mHEwgbeF",
    "https://www.instagram.com/tv/CMjUD1epVWW/": "https://www.instagram.com/p/CMjUD1epVWW",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
