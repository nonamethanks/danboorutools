from collections.abc import Iterator

from danboorutools.logical.sessions.pixiv_sketch import PixivSketchPostData, PixivSketchSession
from danboorutools.logical.urls.pixiv_sketch import _process_post
from danboorutools.models.feed import Feed


class PixivSketchFeed(Feed):
    session = PixivSketchSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[PixivSketchPostData]]:
        json_url = "https://sketch.pixiv.net/api/walls/home.json"

        while True:
            feed_data = self.session.get_page_of_posts(
                json_url,
                headers={"x-requested-with": "https://sketch.pixiv.net/api/walls/home.json"},
            )

            if not feed_data.posts:
                raise NotImplementedError(self)

            yield feed_data.posts

            json_url = feed_data.next_page

    _process_post = _process_post

    @property
    def normalized_url(self) -> str:
        return "https://sketch.pixiv.net/followings"
