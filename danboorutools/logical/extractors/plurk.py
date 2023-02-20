from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class PlurkUrl(Url):
    pass


class PlurkPostUrl(PostUrl, PlurkUrl):
    post_id: str


class PlurkArtistUrl(ArtistUrl, PlurkUrl):
    username: str


class PlurkImageUrl(PostAssetUrl, PlurkUrl):
    image_id: str
