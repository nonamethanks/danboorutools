from __future__ import annotations

import re
from typing import TYPE_CHECKING

from danboorutools.logical.sessions.newgrounds import NewgroundsSession
from danboorutools.logical.urls.newgrounds import NewgroundsPostUrl
from danboorutools.models.feed import Feed

if TYPE_CHECKING:
    from collections.abc import Iterator

    from bs4 import Tag


class NewgroundsFeed(Feed):
    session = NewgroundsSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[Tag]]:
        feed_url = "https://www.newgrounds.com/social/feeds/show/favorite-artists"

        while True:
            posts_page = self.session.get(feed_url).html
            yield posts_page.select(".pod-body a.portal-feed-large-title")

            last_event = min(re.findall(r"feedselector_\w+_\w+_e(\d+)", str(posts_page)))
            feed_url = f"https://www.newgrounds.com/social/feeds/lflw/123456/lfrn/987654/last/{last_event}"

    def _process_post(self, post_object: Tag) -> None:
        post = NewgroundsPostUrl.parse_and_assert(post_object.attrs["href"])

        self._register_post(
            post=post,
            assets=post._extract_assets(),
            score=post.score,
            created_at=post.created_at,
        )
