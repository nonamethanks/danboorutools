from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class PixivSketchUrl(Url):
    pass


class PixivSketchPostUrl(PostUrl, PixivSketchUrl):
    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_id = kwargs["post_id"]
        return f"https://sketch.pixiv.net/items/{post_id}"


class PixivSketchArtistUrl(ArtistUrl, PixivSketchUrl):
    stacc: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        stacc = kwargs["stacc"]
        return f"https://sketch.pixiv.net/@{stacc}"


class PixivSketchImageUrl(PostAssetUrl, PixivSketchUrl):
    ...
