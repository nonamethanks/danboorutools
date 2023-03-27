from collections.abc import Iterator

from danboorutools.logical.sessions.fantia import FantiaSession
from danboorutools.logical.urls.fantia import FantiaPostUrl
from danboorutools.models.feed import Feed


class FantiaFeed(Feed):
    session = FantiaSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[int]]:
        page = 1
        while True:
            page_json = self.session.get_feed(page=page)
            if not page_json["has_next"]:
                return

            yield page_json["posts"]

    def _process_post(self, post_object: dict) -> None:
        post = FantiaPostUrl.build(FantiaPostUrl, post_id=post_object["id"], post_type="posts")

        self._register_post(
            post=post,
            assets=post.post_data.assets,
            score=post.post_data.likes_count,
            created_at=post.post_data.posted_at,
        )
