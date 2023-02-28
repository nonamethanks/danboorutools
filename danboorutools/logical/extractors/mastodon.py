from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class MastodonUrl(Url):
    site: str


class MastodonPostUrl(PostUrl, MastodonUrl):
    post_id: int
    username: str | None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if username := kwargs["username"]:
            return f"https://{kwargs['site']}/@{username}/{kwargs['post_id']}"
        else:
            return f"https://{kwargs['site']}/web/statuses/{kwargs['post_id']}"


class MastodonArtistUrl(ArtistUrl, MastodonUrl):
    username: str | None
    user_id: int | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if username := kwargs["username"]:
            return f"https://{kwargs['site']}/@{username}"
        elif user_id := kwargs["user_id"]:
            return f"https://{kwargs['site']}/web/accounts/{user_id}"  # TODO: maybe split
        else:
            raise NotImplementedError


class MastodonOldImageUrl(RedirectUrl, MastodonUrl):
    filename: str

    normalize_string = "https://{site}/media/{filename}"


class MastodonImageUrl(PostAssetUrl, MastodonUrl):
    subdirs: list[str]

    @property
    def full_size(self) -> str:
        filename = self.parsed_url.url_parts[-1]
        subdirs = ('/').join(self.subdirs)

        if self.parsed_url.url_parts[0] == "system":
            return f"https://{self.parsed_url.hostname}/system/media_attachments/files/{subdirs}/original/{filename}"
        else:
            return f"https://{self.parsed_url.hostname}/media_attachments/files/{subdirs}/original/{filename}"


class MastodonOauthUrl(RedirectUrl, MastodonUrl):
    oauth_id: int

    normalize_string = "https://{site}/oauth_authentications/{oauth_id}"
