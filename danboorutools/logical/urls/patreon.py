from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from danboorutools.exceptions import DeadUrlError, NotAnArtistError
from danboorutools.logical.sessions.patreon import PatreonArtistData, PatreonSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url

if TYPE_CHECKING:
    from collections.abc import Iterator


class PatreonUrl(Url):
    session = PatreonSession()


class PatreonPostUrl(PostUrl, PatreonUrl):
    post_id: int
    title: str | None = None
    username: str | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_id = kwargs["post_id"]
        if title := kwargs.get("title"):
            return f"https://www.patreon.com/posts/{title}-{post_id}"
        else:
            return f"https://www.patreon.com/posts/{post_id}"

    @cached_property
    def gallery(self) -> PatreonArtistUrl:
        if self.username:
            return PatreonArtistUrl.normalize(username=self.username)

        artist_data = self.session.artist_data(self.normalized_url)
        artist_url = PatreonArtistUrl.parse(artist_data.artist_url)
        assert isinstance(artist_url, PatreonArtistUrl)
        return artist_url


class PatreonArtistUrl(ArtistUrl, PatreonUrl):
    username: str | None
    user_id: int | None = None

    def _extract_posts_from_each_page(self) -> Iterator:
        try:
            _ = self.artist_data
        except NotAnArtistError:
            return []
        raise NotImplementedError

    @classmethod
    def normalize(cls, **kwargs) -> str:
        if username := kwargs.get("username"):
            return f"https://www.patreon.com/{username}"
        elif user_id := kwargs.get("user_id"):
            return f"https://www.patreon.com/user?u={user_id}"
        else:
            raise NotImplementedError

    @property
    def artist_data(self) -> PatreonArtistData:
        return self.session.artist_data(self.normalized_url)

    @property
    def related(self) -> list[Url]:
        if self.is_deleted:
            return []
        try:
            return self.artist_data.related_urls
        except NotAnArtistError:
            return []

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []
        try:
            return [self.artist_data.name]
        except NotAnArtistError:
            return []

    @property
    def secondary_names(self) -> list[str]:
        if self.username:
            return [self.username]
        try:
            return [self.artist_data.username] if self.artist_data.username else []
        except NotAnArtistError:
            return []

    def subscribe(self) -> None:
        try:
            username = self.username or self.artist_data.username
        except NotAnArtistError:
            return
        self.session.subscribe(username)

    @cached_property
    def is_deleted(self) -> bool:
        try:
            _ = self.artist_data
        except DeadUrlError:
            return True
        except NotAnArtistError:
            return False
        else:
            return False


class PatreonImageUrl(PostAssetUrl, PatreonUrl):
    post_id: int | None = None

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url  # could be a thumbnail
