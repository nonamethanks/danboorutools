from danboorutools.models.url import ArtistUrl, AssetUrl, PostUrl
from danboorutools.util.misc import compile_url

REGEX_ARTIST = compile_url(r"https?:\/\/sketch\.pixiv.net\/@(?P<artist_id>[\w-]+)")
REGEX_POST = compile_url(r"https?:\/\/sketch\.pixiv\.net\/items\/(?P<post_id>\d+)")
REGEX_IMAGE = compile_url(
    r"https?:\/\/(?:img-sketch.(?:pixiv|pximg).net|sketch.pixiv.net).*?\/uploads\/medium\/file\/\d+\/(?P<image_id>\d+)\.\w")


class PixivSketchPostUrl(PostUrl):
    test_cases = [
        "https://sketch.pixiv.net/items/5835314698645024323",
    ]
    domains = ["pixiv.net"]
    pattern = REGEX_POST
    normalization = "https://sketch.pixiv.net/items/{post_id}"
    id_name = "post_id"


class PixivSketchArtistUrl(ArtistUrl):
    test_cases = [
        "https://sketch.pixiv.net/@user_ejkv8372",
        "https://sketch.pixiv.net/@user_ejkv8372/followings"
    ]
    domains = ["pixiv.net"]
    pattern = REGEX_ARTIST
    normalization = "https://sketch.pixiv.net/@{artist_id}"
    id_name = "artist_id"


class PixivSketchImageUrl(AssetUrl):
    test_cases = [
        "https://img-sketch.pixiv.net/uploads/medium/file/4463372/8906921629213362989.jpg",
        "https://img-sketch.pximg.net/c!/w=540,f=webp:jpeg/uploads/medium/file/4463372/8906921629213362989.jpg",
        "https://img-sketch.pixiv.net/c/f_540/uploads/medium/file/9986983/8431631593768139653.jpg",
    ]
    id_name = "image_id"
    pattern = REGEX_IMAGE
    domains = ["pixiv.net", "pximg.net"]
