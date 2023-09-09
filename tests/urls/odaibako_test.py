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

assert_info_url(
    "https://odaibako.net/u/mitumituami_",
    url_type=OdaibakoUrl,
    url_properties=dict(username="mitumituami_"),
    primary_names=["三ツ三ツ編ミ 🔞のお題箱"],
    secondary_names=["mitumituami_"],
    related=["https://twitter.com/mitumituami_"],
)
