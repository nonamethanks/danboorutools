from danboorutools.logical.extractors.marshmallow_qa import MarshmallowQaUrl
from tests.extractors import generate_parsing_suite

urls = {
    MarshmallowQaUrl: {
        "https://marshmallow-qa.com/_ena_ena_?utm_medium=url_text&utm_sou": "https://marshmallow-qa.com/_ena_ena_",
    },
}


generate_parsing_suite(urls)
