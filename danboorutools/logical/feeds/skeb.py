from collections.abc import Iterator

from danboorutools.logical.sessions.skeb import SkebPostFeedData, SkebSession
from danboorutools.logical.urls.skeb import SkebPostUrl
from danboorutools.models.feed import Feed


class SkebFeed(Feed):
    session = SkebSession()
    quit_early_page = 1

    def _extract_posts_from_each_page(self) -> Iterator[list[SkebPostFeedData]]:
        offset = 0
        limit = None
        while True:
            posts = self.session.get_feed(offset=offset, limit=limit)
            yield posts
            limit = len(posts)
            offset += limit

    def _process_post(self, post_object: SkebPostFeedData) -> None:
        if post_object.private:
            return

        post = SkebPostUrl.parse("https://skeb.jp" + post_object.path)
        assert isinstance(post, SkebPostUrl)

        self._register_post(
            post=post,
            assets=post.assets,
            score=post.score,
            created_at=post.created_at,
        )
