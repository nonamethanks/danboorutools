from danboorutools.logical.urls.bigcartel import BigcartelArtistUrl, BigcartelImageUrl, BigcartelPostUrl
from tests.urls import assert_artist_url, generate_parsing_suite

urls = {
    BigcartelArtistUrl: {
        "http://akaimise.bigcartel.com": "https://akaimise.bigcartel.com",
        "https://msjordankay.bigcartel.com/products": "https://msjordankay.bigcartel.com",
        "https://jeanini.bigcartel.com/category/sleep-san": "https://jeanini.bigcartel.com",
    },
    BigcartelPostUrl: {
        "https://nulliphy.bigcartel.com/product/salmon-run-next-wave-11x17-art-print": "https://nulliphy.bigcartel.com/product/salmon-run-next-wave-11x17-art-print",
    },
    BigcartelImageUrl: {
        # "https://images.bigcartel.com/product_images/199924007/WipIII.png": "https://images.bigcartel.com/product_images/199924007/WipIII.png",
        # "https://assets.bigcartel.com/account_images/5464426/seol_chuseokChibi.png?auto=format&fit=max&h=1200&w=1200": "https://assets.bigcartel.com/account_images/5464426/seol_chuseokChibi.png?auto=format&fit=max&h=1200&w=1200",
    },
}

generate_parsing_suite(urls)

assert_artist_url(
    url="http://akaimise.bigcartel.com",
    url_type=BigcartelArtistUrl,
    url_properties=dict(username="akaimise"),
    primary_names=[],
    secondary_names=["akaimise"],
    related=[],
)
