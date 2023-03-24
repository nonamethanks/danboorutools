from danboorutools.logical.urls.bitly import BitlyUrl
from tests.urls import assert_redirect_url, generate_parsing_suite

urls = {
    BitlyUrl: {
        "https://bit.ly/3xcRBib": "https://bit.ly/3xcRBib",
    },
}


generate_parsing_suite(urls)

assert_redirect_url(
    "https://bit.ly/3xcRBib",
    url_type=BitlyUrl,
    url_properties=dict(redirect_id="3xcRBib"),
    redirects_to="https://www.youtube.com/results?search_query=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8Fch&sp=EgIIBA%253D%253D",
)
