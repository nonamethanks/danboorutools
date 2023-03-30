from collections.abc import Iterator

from danboorutools.logical.sessions.pixiv_sketch import PixivSketchPostData, PixivSketchSession
from danboorutools.logical.urls.pixiv_sketch import PixivSketchArtistUrl, PixivSketchPostUrl
from danboorutools.models.feed import Feed


class PixivSketchFeed(Feed):
    session = PixivSketchSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[PixivSketchPostData]]:
        json_url = "https://sketch.pixiv.net/api/walls/home.json"

        while True:
            feed_data = self.session.get_feed(json_url)

            if not feed_data.posts:
                raise NotImplementedError(self)

            yield feed_data.posts

            json_url = feed_data.next_page

    def _process_post(self, post_object: PixivSketchPostData) -> None:
        post = PixivSketchPostUrl.build(post_id=post_object.id)

        if not post_object.media:
            return

        assets = [i["photo"]["original"]["url"] for i in post_object.media]

        post.artist = PixivSketchArtistUrl.build(stacc=post_object.user["unique_name"])

        self._register_post(
            post=post,
            assets=assets,
            created_at=post_object.created_at,
            score=post_object.feedback_count,
        )