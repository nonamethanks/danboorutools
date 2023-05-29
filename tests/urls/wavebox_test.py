from danboorutools.logical.urls.wavebox import WaveboxUrl
from tests.urls import assert_info_url, generate_parsing_suite

urls = {
    WaveboxUrl: {
        "https://wavebox.me/wave/c5c9yndqm26x5l6f/": "https://wavebox.me/wave/c5c9yndqm26x5l6f/",
    },
}


generate_parsing_suite(urls)

assert_info_url(
    "https://wavebox.me/wave/230rwk0rodc71cu6/",
    url_type=WaveboxUrl,
    url_properties=dict(user_id="230rwk0rodc71cu6"),
    primary_names=["甘粥"],
    secondary_names=[],
    related=[],
)
