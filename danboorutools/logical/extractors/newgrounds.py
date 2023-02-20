from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class NewgroundsUrl(Url):
    pass


class NewgroundsPostUrl(PostUrl, NewgroundsUrl):
    username: str
    title: str


class NewgroundsDumpUrl(PostUrl, NewgroundsUrl):
    dump_id: str


class NewgroundsVideoPostUrl(PostUrl, NewgroundsUrl):
    video_id: int


class NewgroundsArtistUrl(ArtistUrl, NewgroundsUrl):
    username: str


class NewgroundsImageUrl(PostAssetUrl, NewgroundsUrl):
    username: str | None
    title: str | None
