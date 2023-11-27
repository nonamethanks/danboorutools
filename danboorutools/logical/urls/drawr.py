from danboorutools.models.url import ArtistUrl, DeadDomainUrl, PostAssetUrl, PostUrl, Url


class DrawrUrl(DeadDomainUrl, Url):
    ...


class DrawrArtistUrl(ArtistUrl, DrawrUrl):
    username: str

    normalize_template = "https://drawr.net/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []


class DrawrPostUrl(PostUrl, DrawrUrl):
    post_id: int

    normalize_template = "https://drawr.net/show.php?id={post_id}"


class DrawrImageUrl(PostAssetUrl, DrawrUrl):
    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url
