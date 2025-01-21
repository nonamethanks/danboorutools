import pytest

from danboorutools.logical.urls.bitly import BitlyUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestRedirectUrl

urls = {
    BitlyUrl: {
        "https://bit.ly/3xcRBib": "https://bit.ly/3xcRBib",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestBitlyUrl1(_TestRedirectUrl):
    url_string = "https://bit.ly/3xcRBib"
    url_type = BitlyUrl
    url_properties = dict(redirect_id="3xcRBib")
    redirects_to = "https://www.youtube.com/results?search_query=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8Fch&sp=EgIIBA%253D%253D"


class TestBitlyUrl2(_TestRedirectUrl):
    url_string = "https://bit.ly/3m3YHlb"
    url_type = BitlyUrl
    url_properties = dict(redirect_id="3m3YHlb")
    redirects_to = "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG37546.html/options[0]/ENG/options[1]/CHI_HANS/options[2]/NM"
