from collections.abc import Iterator

from danboorutools.logical.sessions.tumblr import TumblrPostData, TumblrSession
from danboorutools.logical.urls.tumblr import TumblrPostUrl
from danboorutools.models.feed import Feed


class TumblrFeed(Feed):
    session = TumblrSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[TumblrPostData]]:
        offset = 0
        limit = 20
        while True:
            posts = self.session.get_feed(limit=limit, offset=offset)
            yield posts
            offset += len(posts)

    def _process_post(self, post_object: TumblrPostData) -> None:
        if post_object.reblogged_root_name:
            return

        post = TumblrPostUrl.build(blog_name=post_object.blog_name, post_id=post_object.id)

        self._register_post(
            post=post,
            assets=post_object.assets,
            score=post_object.note_count,
            created_at=post_object.timestamp,
        )
