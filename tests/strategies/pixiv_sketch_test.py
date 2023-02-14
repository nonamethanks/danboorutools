from ward import test

from danboorutools.logical.strategies.pixiv_sketch import PixivSketchArtistUrl, PixivSketchImageUrl, PixivSketchPostUrl
from tests.strategies import assert_parse_test_cases


@test("Parse pixiv sketch urls", tags=["parsing", "pixivsketch"])
def parsing_test() -> None:
    assert_parse_test_cases(PixivSketchImageUrl)
    assert_parse_test_cases(PixivSketchArtistUrl)
    assert_parse_test_cases(PixivSketchPostUrl)
