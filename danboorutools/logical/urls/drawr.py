from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class DrawrUrl(Url):
    ...


class DrawrArtistUrl(ArtistUrl, DrawrUrl):
    username: str

    normalize_template = "https://drawr.net/{username}"

    is_deleted = True

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []

    def _extract_posts(self) -> None:
        return


class DrawrPostUrl(PostUrl, DrawrUrl):
    post_id: int
    is_deleted = True

    normalize_template = "https://drawr.net/show.php?id={post_id}"


class DrawrImageUrl(PostAssetUrl, DrawrUrl):
    is_deleted = True

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url
