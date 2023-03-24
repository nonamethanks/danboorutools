from danboorutools.logical.urls.odaibako import OdaibakoUrl
from tests.urls import assert_info_url, generate_parsing_suite

urls = {
    OdaibakoUrl: {
        "http://odaibako.net/u/kyou1999080": "https://odaibako.net/u/kyou1999080",
    },
}


generate_parsing_suite(urls)

assert_info_url(
    "https://odaibako.net/u/kazahana__h",
    url_type=OdaibakoUrl,
    url_properties=dict(username="kazahana__h"),
    primary_names=["箱"],
    secondary_names=["kazahana__h"],
    related=["https://twitter.com/kazahana__h"],
)
