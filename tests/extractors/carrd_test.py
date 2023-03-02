from danboorutools.logical.extractors.carrd import CarrdUrl
from tests.extractors import generate_parsing_suite

urls = {
    CarrdUrl: {
        "https://veriea.carrd.co/": "https://veriea.carrd.co",
    }
}


generate_parsing_suite(urls)
