from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from danboorutools.logical.sessions.bluesky import BlueskySession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url, parse_list
from danboorutools.util.misc import extract_urls_from_string

if TYPE_CHECKING:
    from collections.abc import Iterator

    from atproto_client.models.app.bsky.actor.defs import ProfileViewDetailed
    from atproto_client.models.app.bsky.feed.defs import FeedViewPost


class BlueskyUrl(Url):
    session = BlueskySession()


class BlueskyArtistUrl(ArtistUrl, BlueskyUrl):
    username: str

    normalize_template = "https://bsky.app/profile/{username}"

    @cached_property
    def artist_data(self) -> ProfileViewDetailed:
        return self.session.api.get_profile(self.username)

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.display_name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username.removesuffix(".bsky.social")]

    @property
    def related(self) -> list[Url]:
        description = self.artist_data.description

        return list(map(Url.parse, extract_urls_from_string(description)))

    def subscribe(self) -> None:
        self.session.subscribe(self.username)

    def unsubscribe(self) -> None:
        self.session.unsubscribe(self.username)

    def _extract_assets(self) -> list:
        return []

    def _extract_posts_from_each_page(self) -> Iterator[list[FeedViewPost]]:
        cursor = None
        while True:
            resp = self.session.get_posts(self.username, cursor=cursor)
            yield resp.feed
            if not cursor:
                return None
            cursor = resp.cursor

    def _process_post(self, post_object: FeedViewPost) -> None:
        post = post_object.post
        post_id = post.uri.split("/")[-1]
        username = post.author.handle

        post_url = BlueskyPostUrl.build(username=username, post_id=post_id)
        post_url.gallery = self

        assets = parse_list([image.fullsize for image in post.embed.images], BlueskyImageUrl)

        self._register_post(
            post=post_url,
            assets=assets,
            created_at=post.record.created_at,
            score=post.like_count,
        )


class BlueskyPostUrl(PostUrl, BlueskyUrl):
    post_id: str
    username: str

    normalize_template = "https://bsky.app/profile/{username}/post/{post_id}"

    @cached_property
    def gallery(self) -> BlueskyArtistUrl:
        return BlueskyArtistUrl.build(username=self.username)


class BlueskyImageUrl(PostAssetUrl, BlueskyUrl):
    @property
    def full_size(self) -> str:
        if "feed_fullsize" in self.parsed_url.raw_url:
            return self.parsed_url.raw_url.removesuffix("@jpeg").removesuffix("@jpg").removesuffix("@png")
        raise NotImplementedError(self.parsed_url.raw_url)
