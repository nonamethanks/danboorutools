from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class FoundationUrl(Url):
    pass


class FoundationPostUrl(PostUrl, FoundationUrl):
    artist_name: str
    subdir: str
    post_id: int


class FoundationArtistUrl(ArtistUrl, FoundationUrl):
    artist_name: str | None
    artist_hash: str | None = None


class FoundationImageUrl(PostAssetUrl, FoundationUrl):
    file_hash: str | None
    work_id: int | None
    token_id: str | None
