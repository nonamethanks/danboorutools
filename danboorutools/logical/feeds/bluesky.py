from __future__ import annotations

from typing import TYPE_CHECKING

from danboorutools.logical.sessions.bluesky import BlueskySession
from danboorutools.logical.urls.bluesky import BlueskyArtistUrl, BlueskyImageUrl, BlueskyPostUrl
from danboorutools.models.feed import Feed
from danboorutools.models.url import parse_list

if TYPE_CHECKING:
    from collections.abc import Iterator

    from atproto_client.models.app.bsky.feed.defs import FeedViewPost


class BlueskyFeed(Feed):
    session = BlueskySession()

    def _extract_posts_from_each_page(self) -> Iterator[list[FeedViewPost]]:
        cursor = None
        while True:
            resp = self.session.get_feed(cursor=cursor)

            yield resp.feed

            if not cursor:
                return None
            cursor = resp.cursor

    def _process_post(self, post_object: FeedViewPost) -> None:
        if not post_object.post.author.viewer.following:
            return

        if not post_object.post.embed:
            return

        post = post_object.post
        post_id = post.uri.split("/")[-1]
        username = post.author.handle

        post_url = BlueskyPostUrl.build(username=username, post_id=post_id)
        post_url.gallery = BlueskyArtistUrl.build(username=username)

        try:
            img_urls = [image.fullsize for image in post.embed.images]
        except AttributeError as e:
            if post.embed.py_type == "app.bsky.embed.external#view":
                return
            e.add_note(str(post.embed))
            raise

        assets = parse_list(img_urls, BlueskyImageUrl)

        self._register_post(
            post=post_url,
            assets=assets,
            created_at=post.record.created_at,
            score=post.like_count,
        )

    @property
    def normalized_url(self) -> str:
        return "https://bsky.app"
