from __future__ import annotations

from functools import cached_property

from danboorutools.exceptions import UrlIsDeleted
from danboorutools.logical.sessions.mastodon import MastodonArtistData, MastodonSession
from danboorutools.models.url import ArtistUrl, InfoUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class MastodonUrl(Url):
    site: str
    session = MastodonSession()


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
    username: str

    normalize_string = "https://{site}/@{username}"

    @cached_property
    def artist_data(self) -> MastodonArtistData:
        return self.session.user_data(self.site, username=self.username)

    @property
    def user_id_url(self) -> MastodonWebIdUrl:
        return Url.build(MastodonWebIdUrl, user_id=self.artist_data.id, site=self.site)

    @property
    def related(self) -> list[Url]:
        return [self.user_id_url, *self.artist_data.related_urls]

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.display_name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.artist_data.username]

    @property
    def is_deleted(self) -> bool:
        try:
            _ = self.artist_data
        except UrlIsDeleted:
            return True
        else:
            return False


class MastodonWebIdUrl(InfoUrl, MastodonUrl):
    user_id: int

    normalize_string = "https://{site}/web/accounts/{user_id}"

    @cached_property
    def artist_data(self) -> MastodonArtistData:
        return self.session.user_data(self.site, user_id=self.user_id)

    @property
    def username_url(self) -> MastodonArtistUrl:
        return Url.build(MastodonArtistUrl, username=self.artist_data.username, site=self.site)

    @property
    def related(self) -> list[Url]:
        return [self.username_url, *self.artist_data.related_urls]

    @property
    def primary_names(self) -> list[str]:
        return self.username_url.primary_names

    @property
    def secondary_names(self) -> list[str]:
        return self.username_url.secondary_names

    @property
    def is_deleted(self) -> bool:
        try:
            _ = self.artist_data
        except UrlIsDeleted:
            return True
        else:
            return False


class MastodonOldImageUrl(RedirectUrl, MastodonUrl):
    filename: str

    normalize_string = "https://{site}/media/{filename}"


class MastodonImageUrl(PostAssetUrl, MastodonUrl):
    subdirs: list[str]

    @property
    def full_size(self) -> str:
        filename = self.parsed_url.url_parts[-1]
        subdirs = ("/").join(self.subdirs)

        if self.parsed_url.url_parts[0] == "system":
            return f"https://{self.parsed_url.hostname}/system/media_attachments/files/{subdirs}/original/{filename}"
        else:
            return f"https://{self.parsed_url.hostname}/media_attachments/files/{subdirs}/original/{filename}"


class MastodonOauthUrl(RedirectUrl, MastodonUrl):
    oauth_id: int

    normalize_string = "https://{site}/oauth_authentications/{oauth_id}"
