from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class PixivSketchUrl(Url):
    pass


class PixivSketchPostUrl(PostUrl, PixivSketchUrl):
    post_id: int

    normalize_string = "https://sketch.pixiv.net/items/{post_id}"


class PixivSketchArtistUrl(ArtistUrl, PixivSketchUrl):
    stacc: str

    normalize_string = "https://sketch.pixiv.net/@{stacc}"

    @property
    def related(self) -> list[Url]:
        # pylint: disable=import-outside-toplevel
        from danboorutools.logical.extractors.pixiv import PixivStaccUrl

        return [self.build(PixivStaccUrl, stacc=self.stacc)]


class PixivSketchImageUrl(PostAssetUrl, PixivSketchUrl):
    ...
