from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class PixivSketchUrl(Url):
    pass


class PixivSketchPostUrl(PostUrl, PixivSketchUrl):
    normalization = "https://sketch.pixiv.net/items/{post_id}"

    post_id: int


class PixivSketchArtistUrl(ArtistUrl, PixivSketchUrl):
    normalization = "https://sketch.pixiv.net/@{stacc}"

    stacc: str


class PixivSketchImageUrl(PostAssetUrl, PixivSketchUrl):
    ...
