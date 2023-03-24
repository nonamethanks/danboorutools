from danboorutools.logical.urls.carrd import CarrdUrl
from tests.urls import generate_parsing_suite

urls = {
    CarrdUrl: {
        "https://veriea.carrd.co/": "https://veriea.carrd.co",
    }
}


generate_parsing_suite(urls)
