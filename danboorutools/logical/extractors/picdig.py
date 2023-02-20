from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class PicdigUrl(Url):
    pass


class PicdigPostUrl(PostUrl, PicdigUrl):
    project_id: str
    username: str


class PicdigArtistUrl(ArtistUrl, PicdigUrl):
    username: str


class PicdigImageUrl(PostAssetUrl, PicdigUrl):
    account_id: str
    image_id: str
    user_id: str


class PicdigArtistImageUrl(GalleryAssetUrl, PicdigUrl):
    account_id: str
    image_id: str
