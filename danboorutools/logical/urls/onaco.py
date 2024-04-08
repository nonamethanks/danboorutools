from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class OnacoUrl(Url):
    ...


class OnacoArtistUrl(ArtistUrl, OnacoUrl):
    username: str

    normalize_template = "https://onaco.jp/profile/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []


class OnacoPostUrl(PostUrl, OnacoUrl):
    post_id: str

    normalize_template = "https://onaco.jp/detail/{post_id}"


class OnacoImageUrl(PostAssetUrl, OnacoUrl):
    ...
