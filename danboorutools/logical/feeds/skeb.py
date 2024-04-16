from collections.abc import Iterator

from danboorutools.logical.sessions.skeb import SkebPostFromPageData, SkebSession
from danboorutools.logical.urls.skeb import SkebPostUrl
from danboorutools.models.feed import Feed


class SkebFeed(Feed):
    session = SkebSession()
    quit_early_page = 1

    def _extract_posts_from_each_page(self) -> Iterator[list[SkebPostFromPageData]]:
        offset = 0
        limit = None
        while True:
            posts = self.session.get_feed(offset=offset, limit=limit)
            yield posts
            limit = len(posts)
            offset += limit

    def _process_post(self, post_object: SkebPostFromPageData) -> None:
        if post_object.private:
            return

        post = SkebPostUrl.parse_and_assert("https://skeb.jp" + post_object.path)

        self._register_post(
            post=post,
            assets=post._extract_assets(),
            score=post.score,
            created_at=post.created_at,
        )

    @property
    def normalized_url(self) -> str:
        return "https://skeb.jp"
