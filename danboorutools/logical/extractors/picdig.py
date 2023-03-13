from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class PicdigUrl(Url):
    pass


class PicdigPostUrl(PostUrl, PicdigUrl):
    project_id: str
    username: str

    normalize_template = "https://picdig.net/{username}/projects/{project_id}"


class PicdigArtistUrl(ArtistUrl, PicdigUrl):
    username: str
    normalize_template = "https://picdig.net/{username}"


class PicdigImageUrl(PostAssetUrl, PicdigUrl):
    account_id: str
    image_id: str
    user_id: str

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url  # this can be a thumbnail


class PicdigArtistImageUrl(GalleryAssetUrl, PicdigUrl):
    account_id: str
    image_id: str

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url  # this can be a thumbnail
