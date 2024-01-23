from collections.abc import Iterator
from itertools import count

from danboorutools.logical.sessions.artstation import ArtstationSession
from danboorutools.logical.urls.artstation import ArtStationPostUrl
from danboorutools.models.feed import Feed
from danboorutools.models.url import Url


class ArtstationFeed(Feed):
    session = ArtstationSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[str]]:
        return map(self.session.get_post_urls_from_feed, count(1))

    def _process_post(self, post_object: str) -> None:
        post = Url.parse(post_object)
        assert isinstance(post, ArtStationPostUrl)

        self._register_post(
            post=post,
            assets=post._extract_assets(),
            created_at=post.created_at,
            score=post.score,
        )
