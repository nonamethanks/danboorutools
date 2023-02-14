from ward import test

from danboorutools.logical.strategies.deviantart import (DeviantArtArtistUrl, DeviantArtImageUrl, DeviantArtPostUrl, DeviantArtWixmpImage,
                                                         FavMeUrl, StashUrl)
from tests.strategies import assert_parse_test_cases


@test("Parse deviantart urls", tags=["parsing", "deviantart"])
def parsing_test() -> None:
    assert_parse_test_cases(DeviantArtArtistUrl)
    assert_parse_test_cases(DeviantArtImageUrl)
    assert_parse_test_cases(DeviantArtPostUrl)
    assert_parse_test_cases(DeviantArtWixmpImage)
    assert_parse_test_cases(StashUrl)
    assert_parse_test_cases(FavMeUrl)
