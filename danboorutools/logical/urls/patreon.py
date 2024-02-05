from __future__ import annotations

from functools import cached_property
from itertools import repeat
from typing import TYPE_CHECKING

from danboorutools.exceptions import DeadUrlError, NotAnArtistError
from danboorutools.logical.sessions.patreon import PatreonArtistData, PatreonCampaignPostData, PatreonSession
from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url

if TYPE_CHECKING:

    from danboorutools.models.has_posts import HasPosts

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
            return PatreonArtistUrl.build(username=self.username)

        artist_data = self.session.artist_data(self.normalized_url)
        artist_url = PatreonArtistUrl.parse(artist_data.artist_url)
        assert isinstance(artist_url, PatreonArtistUrl)
        return artist_url


def _process_post(self: HasPosts, post_object: tuple[PatreonCampaignPostData, list[dict]]) -> None:
    _post_object, included = post_object
    if not _post_object.attributes.current_user_can_view:
        return

    if not (assets := _post_object.get_assets(included)):
        return

    post_url = _post_object.attributes.patreon_url
    if post_url.startswith("/"):
        post_url = "https://www.patreon.com" + post_url
    post = Url.parse(post_url)
    assert isinstance(post, PatreonPostUrl)

    upgrade_url = _post_object.attributes.upgrade_url
    artist_url = Url.parse("https://patreon.com" + upgrade_url)
    assert isinstance(artist_url, PatreonArtistUrl)
    post.gallery = artist_url

    self._register_post(
        post=post,
        assets=assets,
        created_at=_post_object.attributes.published_at,
        score=_post_object.attributes.like_count,
    )


class PatreonArtistUrl(ArtistUrl, PatreonUrl):
    username: str | None
    user_id: int | None = None

    def _extract_posts_from_each_page(self) -> Iterator[list[tuple[PatreonCampaignPostData, list[dict]]]]:  # fucking patreon
        try:
            _ = self.artist_data
        except NotAnArtistError:
            return

        cursor = None
        prev_cursor = None
        while True:
            page_results = self.session.get_posts(campaign_id=self.campaign_id, cursor=cursor)
            yield list(zip(page_results.data, repeat(page_results.included)))
            cursor = page_results.meta["pagination"]["cursors"]["next"]
            if cursor == prev_cursor:
                return

    _process_post = _process_post

    @property
    def campaign_id(self) -> int:
        return self.user_id or self.artist_data.data.id

    def _extract_assets(self) -> list[PatreonGalleryImageUrl]:
        return [
            self.artist_data.profile_image,
            *self.artist_data.reward_images,
        ]

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
        self.session.subscribe(self.normalized_url)

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


class PatreonGalleryImageUrl(GalleryAssetUrl, PatreonUrl):
    user_id: int

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url  # could be a thumbnail

    @cached_property
    def gallery(self) -> PatreonArtistUrl:
        return PatreonArtistUrl.build(user_id=self.user_id)
