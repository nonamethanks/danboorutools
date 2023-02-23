from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class HentaiFoundryUrl(Url):
    pass


class HentaiFoundryPostUrl(PostUrl, HentaiFoundryUrl):
    username: str
    work_id: int


class HentaiFoundryArtistUrl(ArtistUrl, HentaiFoundryUrl):
    username: str


class HentaiFoundryImageUrl(PostAssetUrl, HentaiFoundryUrl):
    username: str
    work_id: int


class HentaiFoundryOldPostUrl(RedirectUrl, HentaiFoundryUrl):
    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_id = kwargs["post_id"]
        return f"https://www.hentai-foundry.com/pic-{post_id}"
