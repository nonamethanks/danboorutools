from collections.abc import Iterator

from danboorutools.logical.sessions.fanbox import FanboxSession
from danboorutools.logical.urls.fanbox import _process_post
from danboorutools.models.feed import Feed


class FanboxFeed(Feed):
    session = FanboxSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[int]]:
        data_url = "https://api.fanbox.cc/post.listHome?limit=10"
        while True:
            page_json = self.session.get_and_parse_fanbox_json(data_url)

            if not (posts_json := page_json["items"]):
                raise NotImplementedError("No results found. Check cookies.")

            yield [post_json["id"] for post_json in posts_json]

            if not (data_url := page_json["nextUrl"]):
                return

    _process_post = _process_post

    @property
    def normalized_url(self) -> str:
        return "https://www.fanbox.cc"
