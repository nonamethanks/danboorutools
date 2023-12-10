import pytest

from danboorutools.logical.urls.poipiku import PoipikuArtistUrl, PoipikuImageUrl, PoipikuPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl

urls = {
    PoipikuArtistUrl: {
        "https://poipiku.com/IllustListPcV.jsp?ID=9056": "https://poipiku.com/9056/",
        "https://poipiku.com/IllustListGridPcV.jsp?ID=9056": "https://poipiku.com/9056/",
        "https://poipiku.com/6849873": "https://poipiku.com/6849873/",
    },
    PoipikuImageUrl: {
        "https://img.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg_640.jpg": "https://img-org.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg",
        "https://img-org.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg": "https://img-org.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg",
        "https://img.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg_640.jpg": "https://img-org.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg",
        "https://img-org.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg": "https://img-org.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg",
        "https://img.poipiku.com/user_img02/000003310/000007036.jpeg_640.jpg": "https://img-org.poipiku.com/user_img02/000003310/000007036.jpeg",
        "https://img-org.poipiku.com/user_img02/000003310/000007036.jpeg": "https://img-org.poipiku.com/user_img02/000003310/000007036.jpeg",
    },
    PoipikuPostUrl: {
        "https://poipiku.com/6849873/8271386.html": "https://poipiku.com/6849873/8271386.html",
        "https://poipiku.com/3310/7036.html": "https://poipiku.com/3310/7036.html",
        "https://poipiku.com/20566/7204115.html": "https://poipiku.com/20566/7204115.html",
        "https://poipiku.com/20566/007185704.html": "https://poipiku.com/20566/7185704.html",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestPoipikuArtistUrl(_TestArtistUrl):
    url_string = "https://poipiku.com/609078/"
    url_type = PoipikuArtistUrl
    url_properties = dict(user_id=609078)
    primary_names = ["jktomoeee"]
    secondary_names = []
    related = ["https://twitter.com/jktomoeee"]
