from ward import test

from danboorutools.logical.strategies.ehentai import EHentaiGalleryUrl, EHentaiImageUrl, EHentaiPageUrl
from tests.strategies import assert_parse_test_cases


@test("Parse ehentai urls", tags=["parsing", "ehentai"])
def parsing_test() -> None:
    assert_parse_test_cases(EHentaiGalleryUrl)
    assert_parse_test_cases(EHentaiPageUrl)
    assert_parse_test_cases(EHentaiImageUrl)
