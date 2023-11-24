from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class BigcartelUrl(Url):
    ...


class BigcartelArtistUrl(ArtistUrl, BigcartelUrl):
    username: str

    normalize_template = "https://{username}.bigcartel.com"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []


class BigcartelPostUrl(PostUrl, BigcartelUrl):
    username: str
    post_id: str

    normalize_template = "https://{username}.bigcartel.com/product/{post_id}"


class BigcartelImageUrl(PostAssetUrl, BigcartelUrl):
    ...
