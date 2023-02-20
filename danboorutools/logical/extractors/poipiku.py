from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class PoipikuUrl(Url):
    pass


class PoipikuPostUrl(PostUrl, PoipikuUrl):
    user_id: int
    post_id: int


class PoipikuArtistUrl(ArtistUrl, PoipikuUrl):
    user_id: int


class PoipikuImageUrl(PostAssetUrl, PoipikuUrl):
    user_id: int
    post_id: int
    image_hash: str | None
    image_id: int | None
