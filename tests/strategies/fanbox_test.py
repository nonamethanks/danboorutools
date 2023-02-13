from ward import test

from danboorutools.logical.strategies.fanbox import FanboxArtistUrl, FanboxImageUrl, FanboxOldArtistUrl, FanboxOldPostUrl, FanboxPostUrl
from tests.strategies import assert_parse_test_cases


@test("Parse pixiv fanbox urls", tags=["parsing", "fanbox"])
def parsing_test() -> None:
    assert_parse_test_cases(FanboxArtistUrl)
    assert_parse_test_cases(FanboxOldArtistUrl)
    assert_parse_test_cases(FanboxImageUrl)
    assert_parse_test_cases(FanboxPostUrl)
    assert_parse_test_cases(FanboxOldPostUrl)
