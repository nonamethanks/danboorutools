from ward import test

from danboorutools.models.url import Url

urls = {
    "https://poipiku.com/IllustListPcV.jsp?ID=9056": "https://poipiku.com/9056/",
    "https://poipiku.com/IllustListGridPcV.jsp?ID=9056": "https://poipiku.com/9056/",
    "https://poipiku.com/6849873": "https://poipiku.com/6849873/",

    "https://img.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg_640.jpg": "https://img-org.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg",
    "https://img-org.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg": "https://img-org.poipiku.com/user_img02/006849873/008271386_016865825_S968sAh7Y.jpeg",
    "https://img.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg_640.jpg": "https://img-org.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg",
    "https://img-org.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg": "https://img-org.poipiku.com/user_img03/000020566/007185704_nb1cTuA1I.jpeg",
    "https://img.poipiku.com/user_img02/000003310/000007036.jpeg_640.jpg": "https://img-org.poipiku.com/user_img02/000003310/000007036.jpeg",
    "https://img-org.poipiku.com/user_img02/000003310/000007036.jpeg": "https://img-org.poipiku.com/user_img02/000003310/000007036.jpeg",

    "https://poipiku.com/6849873/8271386.html": "https://poipiku.com/6849873/8271386.html",
    "https://poipiku.com/3310/7036.html": "https://poipiku.com/3310/7036.html",
    "https://poipiku.com/20566/7204115.html": "https://poipiku.com/20566/7204115.html",
    "https://poipiku.com/20566/007185704.html": "https://poipiku.com/20566/7185704.html",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
