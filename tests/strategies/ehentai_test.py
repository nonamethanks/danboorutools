from ward import test

from danboorutools.logical.strategies.ehentai import EHentaiGalleryUrl, EHentaiImageUrl, EHentaiPageUrl
from tests.strategies import assert_parsed


@test("Parse ehentai urls", tags=["parsing", "ehentai"])
def ehentai_parsing_test() -> None:
    assert_parsed("https://e-hentai.org/g/618395/0439fa3666/", EHentaiGalleryUrl, 618395)
    assert_parsed("https://e-hentai.org/s/8db045702f/618395-2", EHentaiPageUrl, "8db045702f")
    assert_parsed("https://e-hentai.org/fullimg.php?gid=1709178&page=67&key=9yjdgel9z3l", EHentaiImageUrl)
    assert_parsed("https://ehgt.org/14/63/1463dfbc16847c9ebef92c46a90e21ca881b2a12-1729712-4271-6032-jpg_l.jpg", EHentaiImageUrl)
    assert_parsed("https://ijmfumn.lrwlzmbkzanr.hath.network:2514/h/3eae3a4e3319c5d2477dcb901c69ca1019b75191-120434-1280-1735-jpg/keystamp=1675414800-16624fe708;fileindex=31049863;xres=1280/IMG_0033.jpg", EHentaiImageUrl)  # noqa: E501  # pylint: disable=line-too-long
