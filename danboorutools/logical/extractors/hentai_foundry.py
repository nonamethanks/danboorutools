from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class HentaiFoundryUrl(Url):
    pass


class HentaiFoundryPostUrl(PostUrl, HentaiFoundryUrl):
    username: str
    post_id: int

    normalize_string = "https://www.hentai-foundry.com/pictures/user/{username}/{post_id}"


class HentaiFoundryArtistUrl(ArtistUrl, HentaiFoundryUrl):
    username: str

    normalize_string = "https://www.hentai-foundry.com/user/{username}"


class HentaiFoundryImageUrl(PostAssetUrl, HentaiFoundryUrl):
    username: str
    work_id: int

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url


class HentaiFoundryOldPostUrl(RedirectUrl, HentaiFoundryUrl):
    post_id: int

    normalize_string = "https://www.hentai-foundry.com/pic-{post_id}"
