from danboorutools.models.url import ArtistUrl, DeadDomainUrl, PostUrl, Url


class GooglePlusUrl(DeadDomainUrl, Url):
    site_name = "google+"


class GooglePlusArtistUrl(ArtistUrl, GooglePlusUrl):
    user_id: str

    normalize_template = "https://plus.google.com/{user_id}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        if self.user_id.startswith("+"):
            return [self.user_id.removeprefix("+")]
        return []

    @property
    def related(self) -> list[Url]:
        return []


class GooglePlusPostUrl(PostUrl, GooglePlusUrl):
    user_id: str
    post_id: str

    normalize_template = "https://plus.google.com/{user_id}/posts/{post_id}"

    @property
    def gallery(self) -> GooglePlusArtistUrl:
        return GooglePlusArtistUrl.build(user_id=self.user_id)
