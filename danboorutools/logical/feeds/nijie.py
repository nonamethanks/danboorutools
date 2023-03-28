from collections.abc import Iterator
from datetime import datetime

from bs4 import Tag

from danboorutools.logical.sessions.nijie import NijieSession
from danboorutools.logical.urls.nijie import NijieArtistUrl, NijiePostUrl
from danboorutools.models.feed import Feed


class NijieFeed(Feed):
    session = NijieSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[Tag]]:
        page = 1
        while True:
            base_url = f"https://nijie.info/like_user_view.php?p={page}"
            html = self.session.get_html(base_url)
            posts = html.select("div#center_column div.nijie")

            yield posts

            last_page = int(html.select(".paging-container li a")[-1].text)
            if last_page == page:
                return

            if not posts:
                raise NotImplementedError("No posts found.")

            page += 1

    def _process_post(self, post_object: Tag) -> None:
        img_thumb = post_object.select_one("img.mozamoza")
        post = NijiePostUrl.build(NijiePostUrl, post_id=int(img_thumb["illust_id"]))
        post.gallery = NijieArtistUrl.build(NijieArtistUrl, user_id=int(img_thumb["user_id"]))

        self._register_post(
            post=post,
            assets=post.assets,
            score=post.score,
            created_at=post.created_at,
        )
