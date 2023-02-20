from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class FuraffinityUrl(Url):
    pass


class FuraffinityPostUrl(PostUrl, FuraffinityUrl):
    post_id: int


class FuraffinityArtistUrl(ArtistUrl, FuraffinityUrl):
    username: str


class FuraffinityImageUrl(PostAssetUrl, FuraffinityUrl):
    username: str | None
    post_id: int | None


class FuraffinityArtistImageUrl(GalleryAssetUrl, FuraffinityUrl):
    ...
