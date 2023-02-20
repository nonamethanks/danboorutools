from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class Nicovideo3dUrl(Url):
    pass


class Nicovideo3dPostUrl(PostUrl, Nicovideo3dUrl):
    work_id: int


class Nicovideo3dArtistUrl(ArtistUrl, Nicovideo3dUrl):
    username: str | None = None  # TODO: this is a redirect
    user_id: int | None
