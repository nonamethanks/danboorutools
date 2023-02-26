from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class HentaiFoundryUrl(Url):
    pass


class HentaiFoundryPostUrl(PostUrl, HentaiFoundryUrl):
    username: str
    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://www.hentai-foundry.com/pictures/user/{kwargs['username']}/{kwargs['post_id']}"


class HentaiFoundryArtistUrl(ArtistUrl, HentaiFoundryUrl):
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        return f"https://www.hentai-foundry.com/user/{kwargs['username']}"


class HentaiFoundryImageUrl(PostAssetUrl, HentaiFoundryUrl):
    username: str
    work_id: int

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url


class HentaiFoundryOldPostUrl(RedirectUrl, HentaiFoundryUrl):
    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_id = kwargs["post_id"]
        return f"https://www.hentai-foundry.com/pic-{post_id}"
