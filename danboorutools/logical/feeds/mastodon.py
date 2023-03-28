
from collections.abc import Iterator

from danboorutools.logical.sessions.mastodon import MastodonPostData, MastodonSession
from danboorutools.models.feed import Feed
from danboorutools.models.url import PostUrl, Url


class _MastodonFeed(Feed):
    session = MastodonSession()
    domain: str

    def _extract_posts_from_each_page(self) -> Iterator[list[MastodonPostData]]:
        max_id_for_loop = 0
        while True:
            posts = self.session.get_feed(self.domain, max_id=max_id_for_loop)

            yield posts

            max_id_for_loop = min(posts, key=lambda p: p.id).id

    def _process_post(self, post_object: MastodonPostData) -> None:
        post = Url.parse(post_object.url)
        assert isinstance(post, PostUrl), post_object

        self._register_post(
            post=post,
            assets=post_object.assets,
            score=post_object.favourites_count,
            created_at=post_object.created_at,
        )


class PawooFeed(_MastodonFeed):
    domain = "pawoo.net"


class BaraagFeed(_MastodonFeed):
    domain = "baraag.net"
