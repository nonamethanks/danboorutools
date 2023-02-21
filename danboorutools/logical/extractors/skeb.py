from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class SkebUrl(Url):
    pass


class SkebAbsolutePostUrl(RedirectUrl, SkebUrl):
    absolute_post_id: int


class SkebPostUrl(PostUrl, SkebUrl):
    post_id: int
    username: str


class SkebArtistUrl(ArtistUrl, SkebUrl):
    username: str


class SkebImageUrl(PostAssetUrl, SkebUrl):
    image_uuid: str | None
    page: int | None
    post_id: int | None