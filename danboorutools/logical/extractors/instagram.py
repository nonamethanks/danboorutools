from danboorutools.models.url import ArtistUrl, PostUrl, Url


class InstagramUrl(Url):
    ...


class InstagramPostUrl(PostUrl, InstagramUrl):
    post_id: str

    normalize_string = "https://www.instagram.com/p/{post_id}"


class InstagramArtistUrl(ArtistUrl, InstagramUrl):
    username: str

    normalize_string = "https://www.instagram.com/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return []  # the effort required to get this data is not worth it tbh
