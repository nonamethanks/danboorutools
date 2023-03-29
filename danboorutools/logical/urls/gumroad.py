from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class GumroadUrl(Url):
    pass


class GumroadArtistUrl(ArtistUrl, GumroadUrl):
    username: str

    normalize_template = "https://{username}.gumroad.com"

    @property
    def related(self) -> list[Url]:
        return []

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]


class GumroadPostUrl(PostUrl, GumroadUrl):
    username: str
    post_id: str

    normalize_template = "https://{username}.gumroad.com/l/{post_id}"


class GumroadPostNoArtist(RedirectUrl, GumroadUrl):
    post_id: str

    normalize_template = "https://app.gumroad.com/l/{post_id}"


class GumroadImageUrl(PostAssetUrl, GumroadUrl):
    ...
