import pytest

from danboorutools.logical.artist_finder import ArtistFinder
from danboorutools.models.url import Url


@pytest.mark.parsing
@pytest.mark.artist_finder
def test_artist_name_translation_1() -> None:
    name = "蜘蛛の糸"
    assert ArtistFinder.sanitize_tag_name(name) == "kumo_no_ito"


@pytest.mark.parsing
@pytest.mark.artist_finder
def test_artist_name_translation_2() -> None:
    name = "せいかん＠C103 2日目東タ09b"
    assert ArtistFinder.sanitize_tag_name(name) == "seikan"


@pytest.mark.parsing
@pytest.mark.artist_finder
def test_artist_name_translation_3() -> None:
    name = "大発作"
    assert ArtistFinder.sanitize_tag_name(name) == "daihatsu_saku"


@pytest.mark.parsing
@pytest.mark.artist_finder
def test_artist_name_translation_4() -> None:
    name = "神成迅子"
    assert ArtistFinder.sanitize_tag_name(name) == "shen_cheng_xun_zi"


@pytest.mark.parsing
@pytest.mark.artist_finder
def test_artist_name_translation_5() -> None:
    name = "鱼呆呆呆呆呆"
    assert ArtistFinder.sanitize_tag_name(name) == "yu_ai_ai_ai_ai_ai"


@pytest.mark.scraping
@pytest.mark.artist_finder
def test_artist_url_extraction() -> None:
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
