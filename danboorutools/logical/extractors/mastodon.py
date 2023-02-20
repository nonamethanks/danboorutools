from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class MastodonUrl(Url):
    site: str


class MastodonPostUrl(PostUrl, MastodonUrl):
    post_id: int
    username: str | None


class MastodonArtistUrl(ArtistUrl, MastodonUrl):
    username: str | None
    user_id: int | None = None


class MastodonImageUrl(PostAssetUrl, MastodonUrl):
    ...


class MastodonOauthUrl(RedirectUrl, MastodonUrl):
    oauth_id: int
