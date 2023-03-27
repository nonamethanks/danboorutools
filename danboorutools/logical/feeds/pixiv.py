from itertools import count

from danboorutools.logical.sessions.pixiv import PixivSession
from danboorutools.logical.urls.pixiv import _process_post
from danboorutools.models.feed import Feed


class PixivFeed(Feed):
    session = PixivSession()

    def _extract_posts_from_each_page(self):  # noqa: ANN202
        return map(self.session.get_feed, count())

    _process_post = _process_post
