from danboorutools.logical.urls.amazon import AmazonAuthorUrl, AmazonItemUrl, AmazonShortenerUrl
from tests.urls import generate_parsing_suite

urls = {
    AmazonAuthorUrl: {
        "https://www.amazon.com/stores/author/B0127EHZ7W": "https://www.amazon.com/stores/author/B0127EHZ7W",
        "https://www.amazon.com/stores/Shei-Darksbane/author/B0127EHZ7W": "https://www.amazon.com/stores/author/B0127EHZ7W",
        "https://www.amazon.com/Shei-Darksbane/e/B0127EHZ7W": "https://www.amazon.com/stores/author/B0127EHZ7W",
    },
    AmazonItemUrl: {
        "https://www.amazon.com/dp/B08BWGQ8NP/": "https://www.amazon.com/dp/B08BWGQ8NP",
        "https://www.amazon.com/Yaoi-Hentai-2/dp/1933664010": "https://www.amazon.com/dp/1933664010",
        "https://www.amazon.com/exec/obidos/ASIN/B004U99O9K/ref=nosim/accessuporg-20?SubscriptionId=1MNS6Z3H8Y5Q5XCMG582\u0026linkCode=xm2\u0026creativeASIN=B004U99O9K": "https://www.amazon.com/dp/B004U99O9K",
        "https://www.amazon.com/gp/product/B08CTJWTMR": "https://www.amazon.com/dp/B08CTJWTMR",
        " https://amazon.jp/o/ASIN/B000P29X0G/ref=nosim/conoco-22": " https://www.amazon.com/dp/B000P29X0G",
    },
    AmazonShortenerUrl: {
        "https://amzn.to/3iZ9vyT": "https://amzn.to/3iZ9vyT",
    },
}


generate_parsing_suite(urls)
