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
    work_id: int

    normalization = "https://www.hentai-foundry.com/pic-{work_id}"