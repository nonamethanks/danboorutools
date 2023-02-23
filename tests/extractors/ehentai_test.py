import re
from typing import TYPE_CHECKING

from ward import test

from danboorutools.logical.extractors.ehentai import EHentaiGalleryUrl, EHentaiImageUrl, EHentaiPageUrl
from danboorutools.models.url import Url
from tests.extractors import generate_gallery_test_suite

if TYPE_CHECKING:
    from tests.extractors import ArtistTestKwargs, GalleryTestKwargs, PostAssetTestKwargs, PostTestKwargs  # noqa


tests = generate_gallery_test_suite(
    url_type=EHentaiGalleryUrl,
    url="https://e-hentai.org/g/182146/4f5c26749f",
    post_count=83,
    url_properties=dict(gallery_id=182146, gallery_token="4f5c26749f"),

    post=dict(
        url_type=EHentaiPageUrl,
        url="https://e-hentai.org/s/b6518716a0/182146-4",
        asset_count=1,
        score=104,
        created_at="2009-12-07 20:25:00",
        url_properties=dict(gallery_id=182146, page_number=4, page_token="b6518716a0"),
        asset=dict(
            url_type=EHentaiImageUrl,
            url=re.compile(r"fullimg\.php\?gid=182146&page=4&key="),
            created_at="2009-12-07 20:25:00",
            url_properties=dict(gallery_id=182146, page_number=4),
            file_md5="5b2a4f60565048d8edd16c65d293cbd1",
        )
    )
)

for test_type, test_method in tests.items():
    @test(f"Scrape a ehentai {test_type}", tags=["scraping", "ehentai", test_type])  # pylint: disable=cell-var-from-loop
    def _(_test_method=test_method) -> None:
        _test_method()


@ test("Deleted urls", tags=["scraping", "ehentai", "deleted"])
def test_deleted() -> None:
    url = Url.parse("https://e-hentai.org/s/8053bb2877/204042-15")
    assert url.is_deleted
    assert url.normalized_url == "https://e-hentai.org/s/8053bb2877/204042-15"  # don't turn to exentai if it's deleted


urls = {
    "https://exhentai.org/g/1858690/b62c996bb6/": "https://exhentai.org/g/1858690/b62c996bb6",
    "http://g.e-hentai.org/g/1858690/b62c996bb6/": "https://e-hentai.org/g/1858690/b62c996bb6",
    "http://e-hentai.org/g/1858690/b62c996bb6/": "https://e-hentai.org/g/1858690/b62c996bb6",
    "http://g.e-hentai.org/g/340478/057192d561/?p=15": "https://e-hentai.org/g/340478/057192d561",

    # "https://exhentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg": "https://exhentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg",
    # "https://e-hentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg": "https://e-hentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg",
    # "https://g.e-hentai.org/?f_shash=85f4d25b291210a2a6936331a1e7202741392715\u0026fs_from=_039.jpg": "https://e-hentai.org/?f_shash=85f4d25b291210a2a6936331a1e7202741392715\u0026fs_from=_039.jpg",
    "https://exhentai.org/fullimg.php?gid=2464842&page=2&key=uinj32c9zag": "https://exhentai.org/fullimg.php?gid=2464842&page=2&key=uinj32c9zag",

    "https://e-hentai.org/s/ad41a3fac6/847994-352": "https://e-hentai.org/s/ad41a3fac6/847994-352",
    "https://exhentai.org/s/ad41a3fac6/847994-352": "https://exhentai.org/s/ad41a3fac6/847994-352",
    "https://g.e-hentai.org/s/ad41a3fac6/847994-352": "https://e-hentai.org/s/ad41a3fac6/847994-352",
    "https://e-hentai.org/s/0251bc4e84/136116-25.jpg": "https://e-hentai.org/s/0251bc4e84/136116-25",

    # "https://ijmwujr.grduyvrrtxiu.hath.network:40162/h/5bf1c8b26c4d0d35951b7116d151209f6784420e-137816-810-1228-jpg/keystamp=1676307900-1fa0db7a58;fileindex=120969163;xres=2400/4134835_103198602_p0.jpg": "https://ijmwujr.grduyvrrtxiu.hath.network:40162/h/5bf1c8b26c4d0d35951b7116d151209f6784420e-137816-810-1228-jpg/keystamp=1676307900-1fa0db7a58;fileindex=120969163;xres=2400/4134835_103198602_p0.jpg",

    # "http://gt2.ehgt.org/a8/9a/a89a1ecc242a1f64edc56bf253442f46e937cdf3-578970-1000-1000-jpg_m.jpg": "http://gt2.ehgt.org/a8/9a/a89a1ecc242a1f64edc56bf253442f46e937cdf3-578970-1000-1000-jpg_m.jpg",
}

for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
