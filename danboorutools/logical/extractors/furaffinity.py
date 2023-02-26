from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url


class FuraffinityUrl(Url):
    pass


class FuraffinityPostUrl(PostUrl, FuraffinityUrl):
    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://www.furaffinity.net/view/{kwargs['post_id']}"


class FuraffinityArtistUrl(ArtistUrl, FuraffinityUrl):
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://www.furaffinity.net/user/{kwargs['username']}"


class FuraffinityImageUrl(PostAssetUrl, FuraffinityUrl):
    username: str | None
    post_id: int | None

    @property
    def full_size(self) -> str:
        if self.parsed_url.subdomain == "d":
            return self.parsed_url.raw_url
        else:
            raise NotImplementedError


class FuraffinityArtistImageUrl(GalleryAssetUrl, FuraffinityUrl):
    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url
