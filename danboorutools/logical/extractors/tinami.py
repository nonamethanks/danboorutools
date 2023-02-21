from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class TinamiUrl(Url):
    pass


class TinamiPostUrl(PostUrl, TinamiUrl):
    post_id: int


class TinamiComicUrl(PostUrl, TinamiUrl):
    comic_id: int
    comic_title: str


class TinamiArtistUrl(ArtistUrl, TinamiUrl):
    profile_id: int | None
    user_id: int | None


class TinamiImageUrl(PostAssetUrl, TinamiUrl):
    ...
