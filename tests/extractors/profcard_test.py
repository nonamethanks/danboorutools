from danboorutools.logical.extractors.profcard import ProfcardUrl
from tests.extractors import generate_parsing_suite

urls = {
    ProfcardUrl: {
        "https://profcard.info/u/73eXlzsmfbXKmCjqJo4SeyNE2SN2": "https://profcard.info/u/73eXlzsmfbXKmCjqJo4SeyNE2SN2",
    },
}

generate_parsing_suite(urls)
