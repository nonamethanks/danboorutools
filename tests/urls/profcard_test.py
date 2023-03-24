from danboorutools.logical.urls.profcard import ProfcardUrl
from tests.urls import assert_info_url, generate_parsing_suite

urls = {
    ProfcardUrl: {
        "https://profcard.info/u/73eXlzsmfbXKmCjqJo4SeyNE2SN2": "https://profcard.info/u/73eXlzsmfbXKmCjqJo4SeyNE2SN2",
    },
}

generate_parsing_suite(urls)

assert_info_url(
    "https://profcard.info/u/73eXlzsmfbXKmCjqJo4SeyNE2SN2",
    url_type=ProfcardUrl,
    url_properties=dict(user_id="73eXlzsmfbXKmCjqJo4SeyNE2SN2"),
    primary_names=["巴"],
    secondary_names=[],
    related=["https://poipiku.com/609078/"],
)
