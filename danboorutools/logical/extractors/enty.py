from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class EntyUrl(Url):
    pass


class EntyPostUrl(PostUrl, EntyUrl):
    post_id: int


class EntyArtistUrl(ArtistUrl, EntyUrl):
    username: str | None
    user_id: int | None


class EntyImageUrl(PostAssetUrl, EntyUrl):
    post_id: int


class EntyArtistImageUrl(GalleryAssetUrl, EntyUrl):
    user_id: int
