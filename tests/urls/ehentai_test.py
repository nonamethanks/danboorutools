import pytest

from danboorutools.logical.urls.ehentai import EHentaiGalleryUrl, EHentaiImageUrl, EHentaiPageUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestGalleryUrl, _TestPostUrl

urls = {
    EHentaiGalleryUrl: {
        "https://exhentai.org/g/1858690/b62c996bb6/": "https://exhentai.org/g/1858690/b62c996bb6",
        "http://g.e-hentai.org/g/1858690/b62c996bb6/": "https://e-hentai.org/g/1858690/b62c996bb6",
        "http://e-hentai.org/g/1858690/b62c996bb6/": "https://e-hentai.org/g/1858690/b62c996bb6",
        "http://g.e-hentai.org/g/340478/057192d561/?p=15": "https://e-hentai.org/g/340478/057192d561",
    },
    EHentaiImageUrl: {
        "https://exhentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg": "",
        "https://e-hentai.org/t/ac/c6/acc6ee51f27416c3052380dabeea175afb272755-71280-640-880-png_l.jpg": "",
        "https://g.e-hentai.org/?f_shash=85f4d25b291210a2a6936331a1e7202741392715\u0026fs_from=_039.jpg": "",
        "https://exhentai.org/fullimg.php?gid=2464842&page=2&key=uinj32c9zag": "https://exhentai.org/fullimg.php?gid=2464842&page=2&key=uinj32c9zag",
        "http://gt2.ehgt.org/a8/9a/a89a1ecc242a1f64edc56bf253442f46e937cdf3-578970-1000-1000-jpg_m.jpg": "",
        "https://ijmwujr.grduyvrrtxiu.hath.network:40162/h/5bf1c8b26c4d0d35951b7116d151209f6784420e-137816-810-1228-jpg/keystamp=1676307900-1fa0db7a58;fileindex=120969163;xres=2400/4134835_103198602_p0.jpg": "",

    },
    EHentaiPageUrl: {
        "https://e-hentai.org/s/ad41a3fac6/847994-352": "https://e-hentai.org/s/ad41a3fac6/847994-352",
        "https://exhentai.org/s/ad41a3fac6/847994-352": "https://exhentai.org/s/ad41a3fac6/847994-352",
        "https://g.e-hentai.org/s/ad41a3fac6/847994-352": "https://e-hentai.org/s/ad41a3fac6/847994-352",
        "https://e-hentai.org/s/0251bc4e84/136116-25.jpg": "https://e-hentai.org/s/0251bc4e84/136116-25",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestEHentaiGalleryUrl(_TestGalleryUrl):
    url_string = "https://e-hentai.org/g/182146/4f5c26749f"
    url_type = EHentaiGalleryUrl
    post_count = 83
    url_properties = dict(gallery_id=182146, gallery_token="4f5c26749f")  # noqa: S106
    posts = ["https://e-hentai.org/s/b6518716a0/182146-4"]


class TestEHentaiPageUrl1(_TestPostUrl):
    url_type = EHentaiPageUrl
    url_string = "https://e-hentai.org/s/b6518716a0/182146-4"
    asset_count = 1
    score = 104
    created_at = "2009-12-07 20:25:00"
    url_properties = dict(gallery_id=182146, page_number=4, page_token="b6518716a0")  # noqa: S106
    assets = [r"fullimg\.php\?gid=182146&page=4&key="]
    md5s = ["5b2a4f60565048d8edd16c65d293cbd1"]


class TestEHentaiPageUrl2:
    url_type = EHentaiPageUrl
    url_string = "https://e-hentai.org/s/8053bb2877/204042-15"
    url_properties = dict(gallery_id=204042, page_number=15, page_token="8053bb2877")  # noqa: S106
    is_deleted = True
