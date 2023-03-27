from collections.abc import Iterator

from danboorutools.logical.sessions.hentai_foundry import HentaiFoundrySession
from danboorutools.logical.urls.hentai_foundry import HentaiFoundryPostUrl
from danboorutools.models.feed import Feed


class HentaiFoundryFeed(Feed):
    session = HentaiFoundrySession()

    def _extract_posts_from_each_page(self) -> Iterator[list[HentaiFoundryPostUrl]]:
        page = 1
        previous_posts: list[HentaiFoundryPostUrl] = []
        while True:
            posts = self.session.get_feed_posts(page=page)
            if posts == previous_posts:
                return
            previous_posts = posts

            yield posts

            page += 1

    def _process_post(self, post_object: HentaiFoundryPostUrl) -> None:
        post = post_object

        self._register_post(
            post=post,
            assets=post.assets,
            score=post.score,
            created_at=post.created_at,
        )
