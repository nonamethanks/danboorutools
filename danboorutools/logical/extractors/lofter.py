from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class LofterUrl(Url):
    pass


class LofterPostUrl(PostUrl, LofterUrl):
    username: str
    post_id: str


class LofterArtistUrl(ArtistUrl, LofterUrl):
    username: str


class LofterImageUrl(PostAssetUrl, LofterUrl):
    ...
