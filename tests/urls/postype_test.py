import pytest

from danboorutools.logical.urls import postype as p
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    p.PostypeArtistUrl: {
        "https://muacmm.postype.com/": "https://www.postype.com/@muacmm",
        "https://peonrin.postype.com/series": "https://www.postype.com/@peonrin",
        "https://peonrin.postype.com/@peonrin": "https://www.postype.com/@peonrin",
    },
    p.PostypeSeriesUrl: {
        "https://soojaeng.postype.com/series/626542": "https://www.postype.com/@soojaeng/series/626542",
        "https://purple-blur.postype.com/series/949574/%EC%86%8C%EB%8B%89%EB%A7%8C%ED%99%94%EC%97%B0%EC%84%B1": "https://www.postype.com/@purple-blur/series/949574",
    },
    p.PostypeBadArtistUrl: {
        "https://www.postype.com/profile/@6qyflt": "https://www.postype.com/profile/@6qyflt",
        "https://www.postype.com/profile/@efuki0/posts": "https://www.postype.com/profile/@efuki0",
    },
    p.PostypePostUrl: {
        "https://tumitumico.postype.com/post/12134471": "https://www.postype.com/@tumitumico/post/12134471",
        "https://www.postype.com/@tumitumico/post/12134471": "https://www.postype.com/@tumitumico/post/12134471",
    },
    p.PostypeImageUrl: {
        "http://i.postype.com/2016/12/27/01/52/0a88e4fef1f92974d3834511120492c8.png?w=1000": "http://i.postype.com/2016/12/27/01/52/0a88e4fef1f92974d3834511120492c8.png",
        "https://d2ufj6gm1gtdrc.cloudfront.net/2024/01/30/14/59/11d8ec943f17a4ede8ae6c13bcc48bb3.png?w=1200&q=90": "https://d2ufj6gm1gtdrc.cloudfront.net/2024/01/30/14/59/11d8ec943f17a4ede8ae6c13bcc48bb3.png",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestPostypeArtistUrl(_TestArtistUrl):
    url_string = "https://seonforest.postype.com/"
    url_type = p.PostypeArtistUrl
    url_properties = dict(username="seonforest")
    primary_names = ["SeonForest @seon_f"]
    secondary_names = ["seonforest"]
    related = ["https://twitter.com/seon_f"]
