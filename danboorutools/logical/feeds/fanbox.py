from collections.abc import Iterator

from danboorutools.logical.sessions.fanbox import FanboxSession
from danboorutools.logical.urls.fanbox import FanboxPostUrl
from danboorutools.models.feed import Feed


class FanboxFeed(Feed):
    session = FanboxSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[int]]:
        data_url = "https://api.fanbox.cc/post.listHome?limit=10"
        while True:
            page_json = self.session.get_and_parse_fanbox_json(data_url, use_cookies=True)

            if not (posts_json := page_json["items"]):
                raise NotImplementedError("No results found. Check cookies.")

            yield [post_json["id"] for post_json in posts_json]

            if not (data_url := page_json["nextUrl"]):
                return

    def _process_post(self, post_object: int) -> None:
        post_data = self.session.post_data(post_object)

        post = FanboxPostUrl.build(username=post_data.creatorId, post_id=post_data.id)

        self._register_post(
            post=post,
            assets=post_data.assets,
            score=post_data.likeCount,
            created_at=post_data.publishedDatetime,
        )
