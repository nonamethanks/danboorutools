from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class TwitterUrl(Url):
    pass


class TwitterPostUrl(PostUrl, TwitterUrl):
    post_id: int
    username: str | None


class TwitterArtistUrl(ArtistUrl, TwitterUrl):
    username: str


class TwitterAssetUrl(PostAssetUrl, TwitterUrl):
    ...


class TwitterIntentUrl(RedirectUrl, TwitterUrl):
    intent_id: int


class TwitterArtistImageUrl(GalleryAssetUrl, TwitterUrl):
    user_id: int


class TwitterShortenerUrl(RedirectUrl, TwitterUrl):
    shortener_id: str
