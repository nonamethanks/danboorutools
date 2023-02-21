from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class PatreonUrl(Url):
    pass


class PatreonPostUrl(PostUrl, PatreonUrl):
    post_id: int
    title: str | None = None
    username: str | None = None


class PatreonArtistUrl(ArtistUrl, PatreonUrl):
    user_id: int | None = None
    username: str | None


class PatreonImageUrl(PostAssetUrl, PatreonUrl):
    post_id: int | None = None
