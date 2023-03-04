from danboorutools.logical.extractors.odaibako import OdaibakoUrl
from tests.extractors import generate_parsing_suite

urls = {
    OdaibakoUrl: {
        "http://odaibako.net/u/kyou1999080": "https://odaibako.net/u/kyou1999080",
    },
}


generate_parsing_suite(urls)
