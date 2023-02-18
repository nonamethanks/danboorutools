from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class ArcaLiveUrl(Url):
    pass


class ArcaLivePostUrl(PostUrl, ArcaLiveUrl):
    post_id: int
    channel: str


class ArcaLiveArtistUrl(ArtistUrl, ArcaLiveUrl):
    user_id: int | None
    username: str


class ArcaLiveImageUrl(PostAssetUrl, ArcaLiveUrl):
    date_string: str
    filename: str
