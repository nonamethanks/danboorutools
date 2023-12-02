import pytest

from danboorutools.logical.urls.bigcartel import BigcartelArtistUrl, BigcartelImageUrl, BigcartelPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    BigcartelArtistUrl: {
        "http://akaimise.bigcartel.com": "https://akaimise.bigcartel.com",
        "https://msjordankay.bigcartel.com/products": "https://msjordankay.bigcartel.com",
        "https://jeanini.bigcartel.com/category/sleep-san": "https://jeanini.bigcartel.com",
    },
    BigcartelPostUrl: {
        "https://nulliphy.bigcartel.com/product/salmon-run-next-wave-11x17-art-print": "https://nulliphy.bigcartel.com/product/salmon-run-next-wave-11x17-art-print",
    },
    BigcartelImageUrl: {
        "https://images.bigcartel.com/product_images/199924007/WipIII.png": "",
        "https://assets.bigcartel.com/account_images/5464426/seol_chuseokChibi.png?auto=format&fit=max&h=1200&w=1200": "",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_artist_url_1():
    generate_artist_test(
        url_string="http://akaimise.bigcartel.com",
        url_type=BigcartelArtistUrl,
        url_properties=dict(username="akaimise"),
        primary_names=[],
        secondary_names=["akaimise"],
        related=[],
    )
