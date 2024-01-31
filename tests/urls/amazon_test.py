import pytest

from danboorutools.logical.urls.amazon import AmazonAuthorUrl, AmazonItemUrl, AmazonShortenerUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    AmazonAuthorUrl: {
        "https://www.amazon.com/stores/author/B0127EHZ7W": "https://www.amazon.com/stores/author/B0127EHZ7W",
        "https://www.amazon.com/stores/Shei-Darksbane/author/B0127EHZ7W": "https://www.amazon.com/stores/author/B0127EHZ7W",
        "https://www.amazon.com/Shei-Darksbane/e/B0127EHZ7W": "https://www.amazon.com/stores/author/B0127EHZ7W",
        "https://www.amazon.co.jp/kindle-dbs/entity/author/B00J2FHN3Q?_encoding=UTF8&offset=0&pageSize=12&searchAlias=stripbooks&sort=date-desc-rank&page=1&langFilter=default#formatSelectorHeader": "https://www.amazon.co.jp/stores/author/B00J2FHN3Q",
    },
    AmazonItemUrl: {
        "https://www.amazon.com/dp/B08BWGQ8NP/": "https://www.amazon.com/dp/B08BWGQ8NP",
        "https://www.amazon.com/Yaoi-Hentai-2/dp/1933664010": "https://www.amazon.com/dp/1933664010",
        "https://www.amazon.com/exec/obidos/ASIN/B004U99O9K/ref=nosim/accessuporg-20?SubscriptionId=1MNS6Z3H8Y5Q5XCMG582\u0026linkCode=xm2\u0026creativeASIN=B004U99O9K": "https://www.amazon.com/dp/B004U99O9K",
        "https://www.amazon.com/gp/product/B08CTJWTMR": "https://www.amazon.com/dp/B08CTJWTMR",
        "https://amazon.jp/o/ASIN/B000P29X0G/ref=nosim/conoco-22": "https://www.amazon.jp/dp/B000P29X0G",
    },
    AmazonShortenerUrl: {
        "https://amzn.to/3iZ9vyT": "https://amzn.to/3iZ9vyT",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestAmazonAuthorUrl(_TestArtistUrl):
    url_string = "https://www.amazon.co.jp/stores/author/B00J2FHN3Q"
    url_type = AmazonAuthorUrl
    url_properties = dict(author_id="B00J2FHN3Q", subsite="co.jp")
    primary_names = ["森小太郎"]
    secondary_names = []
    related = []
