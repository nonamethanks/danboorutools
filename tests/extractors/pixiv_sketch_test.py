from ward import test

from danboorutools.logical.extractors.pixiv_sketch import PixivSketchArtistUrl
from danboorutools.models.url import Url
from tests.extractors import assert_artist_url

urls = {
    "https://img-sketch.pximg.net/c!/w=540,f=webp:jpeg/uploads/medium/file/4463372/8906921629213362989.jpg": "https://img-sketch.pixiv.net/uploads/medium/file/4463372/8906921629213362989.jpg",

    "https://img-sketch.pixiv.net/uploads/medium/file/4463372/8906921629213362989.jpg": "https://img-sketch.pixiv.net/uploads/medium/file/4463372/8906921629213362989.jpg",
    "https://img-sketch.pixiv.net/c/f_540/uploads/medium/file/9986983/8431631593768139653.jpg": "https://img-sketch.pixiv.net/uploads/medium/file/9986983/8431631593768139653.jpg",

    "https://sketch.pixiv.net/items/5835314698645024323": "https://sketch.pixiv.net/items/5835314698645024323",

    "https://sketch.pixiv.net/@user_ejkv8372": "https://sketch.pixiv.net/@user_ejkv8372",
    "https://sketch.pixiv.net/@user_ejkv8372/followings": "https://sketch.pixiv.net/@user_ejkv8372",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string


assert_artist_url(
    "https://sketch.pixiv.net/@interplanetary",
    url_type=PixivSketchArtistUrl,
    url_properties=dict(stacc="interplanetary"),
    primary_names=[],
    secondary_names=["interplanetary"],
    related=["https://www.pixiv.net/stacc/interplanetary"],
    is_deleted=True,
)
