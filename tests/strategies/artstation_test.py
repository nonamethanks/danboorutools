from ward import test

from danboorutools.logical.strategies.artstation import ArtStationArtistUrl, ArtStationImageUrl, ArtStationOldPostUrl, ArtStationPostUrl
from tests.strategies import assert_parse_test_cases


@test("Parse artstation urls", tags=["parsing", "artstation"])
def parsing_test() -> None:
    assert_parse_test_cases(ArtStationArtistUrl)
    assert_parse_test_cases(ArtStationImageUrl)
    assert_parse_test_cases(ArtStationPostUrl)
    assert_parse_test_cases(ArtStationOldPostUrl)
