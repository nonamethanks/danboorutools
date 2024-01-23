from collections.abc import Iterator
from itertools import count

from danboorutools.logical.sessions.ko_fi import KoFiSession
from danboorutools.logical.urls.ko_fi import KoFiPostUrl
from danboorutools.models.feed import Feed


class KoFiFeed(Feed):
    session = KoFiSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[KoFiPostUrl]]:
        return map(self.session.get_feed, count(0))

    def _process_post(self, post_object: KoFiPostUrl) -> None:
        post = post_object

        self._register_post(
            post=post,
            assets=post._extract_assets(),
            score=post.score,
            created_at=post.created_at,
        )
