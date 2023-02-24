from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class LofterUrl(Url):
    pass


class LofterPostUrl(PostUrl, LofterUrl):
    username: str
    post_id: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://{kwargs['username']}.lofter.com/post/{kwargs['post_id']}"


class LofterArtistUrl(ArtistUrl, LofterUrl):
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://{kwargs['username']}.lofter.com"


class LofterImageUrl(PostAssetUrl, LofterUrl):
    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_params
