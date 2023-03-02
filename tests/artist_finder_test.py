from ward import test

from danboorutools.logical.artist_finder import ArtistFinder
from danboorutools.models.url import Url


@test("Artist name romanization", tags=["normalization", "artist_finder"])
def _() -> None:
    name = "蜘蛛の糸"
    assert ArtistFinder.sanitize_tag_name(name) == "kumo_no_ito"


@test("Full crawling", tags=["scraping", "artist_finder"])
def _() -> None:
    url = Url.parse("https://www.pixiv.net/en/users/25687133")

    results = [u.normalized_url for u in ArtistFinder.extract_related_urls_recursively(url)]  # type: ignore[arg-type]
    expected = [
        "https://www.pixiv.net/en/users/25687133",
        "https://www.pixiv.net/stacc/user_zxpv8824",
        "https://sketch.pixiv.net/@user_zxpv8824",
        "https://twitter.com/ROLE_re",
        "https://twitter.com/intent/user?user_id=553357317",
        "https://com.nicovideo.jp/community/co3810467",
    ]

    assert all(expected_url in results for expected_url in expected)
