from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class AfdianUrl(Url):
    pass


class AfdianPostUrl(PostUrl, AfdianUrl):
    post_id: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        return f"https://afdian.net/p/{kwargs['post_id']}"


class AfdianArtistUrl(ArtistUrl, AfdianUrl):
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        return f"https://afdian.net/a/{kwargs['username']}"


class AfdianImageUrl(PostAssetUrl, AfdianUrl):
    user_id: str

    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_params


class AfdianArtistImageUrl(GalleryAssetUrl, AfdianUrl):
    user_id: str

    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_params
