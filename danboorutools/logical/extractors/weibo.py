from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class WeiboUrl(Url):
    pass


class WeiboPostUrl(PostUrl, WeiboUrl):
    illust_long_id: int | None = None
    illust_base62_id: str | None = None
    artist_short_id: int | None = None


class WeiboArtistUrl(ArtistUrl, WeiboUrl):
    artist_short_id: int | None = None
    artist_long_id: int | None = None
    username: str | None = None


class WeiboImageUrl(PostAssetUrl, WeiboUrl):
    ...
