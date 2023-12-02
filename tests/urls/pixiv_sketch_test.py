import pytest

from danboorutools.logical.urls.pixiv_sketch import PixivSketchArtistUrl, PixivSketchImageUrl, PixivSketchPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    PixivSketchImageUrl: {
        "https://img-sketch.pximg.net/c!/w=540,f=webp:jpeg/uploads/medium/file/4463372/8906921629213362989.jpg": "https://img-sketch.pixiv.net/uploads/medium/file/4463372/8906921629213362989.jpg",

        "https://img-sketch.pixiv.net/uploads/medium/file/4463372/8906921629213362989.jpg": "https://img-sketch.pixiv.net/uploads/medium/file/4463372/8906921629213362989.jpg",
        "https://img-sketch.pixiv.net/c/f_540/uploads/medium/file/9986983/8431631593768139653.jpg": "https://img-sketch.pixiv.net/uploads/medium/file/9986983/8431631593768139653.jpg",

    },
    PixivSketchPostUrl: {
        "https://sketch.pixiv.net/items/5835314698645024323": "https://sketch.pixiv.net/items/5835314698645024323",
    },
    PixivSketchArtistUrl: {
        "https://sketch.pixiv.net/@user_ejkv8372": "https://sketch.pixiv.net/@user_ejkv8372",
        "https://sketch.pixiv.net/@user_ejkv8372/followings": "https://sketch.pixiv.net/@user_ejkv8372",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_artist_url_1():
    generate_artist_test(
        url_string="https://sketch.pixiv.net/@interplanetary",
        url_type=PixivSketchArtistUrl,
        url_properties=dict(stacc="interplanetary"),
        primary_names=[],
        secondary_names=["interplanetary"],
        related=["https://www.pixiv.net/stacc/interplanetary"],
        is_deleted=True,
    )
