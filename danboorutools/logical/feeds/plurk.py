import re
from collections.abc import Iterator
from urllib.parse import urljoin

from danboorutools.logical.sessions.plurk import PlurkPostData, PlurkSession
from danboorutools.logical.urls.plurk import PlurkPostUrl
from danboorutools.models.feed import Feed
from danboorutools.models.url import Url
from danboorutools.util.misc import extract_urls_from_string


class PlurkFeed(Feed):
    session = PlurkSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[PlurkPostData]]:
        offset = None
        while True:
            plurks = self.session.get_feed(offset=offset)
            assert plurks
            if not plurks:
                return
            yield plurks

            offset = plurks[-1].posted.isoformat()

    def _process_post(self, post_object: PlurkPostData) -> None:
        if post_object.is_repost:
            return

        post = PlurkPostUrl.build(post_id=post_object.encoded_post_id)

        image_thumbs = post.html.select(".bigplurk .content a:not(.ex_link) img, .response.highlight_owner .content a:not(.ex_link) img")

        images = [img_html.get("alt") or img_html.get("src") for img_html in image_thumbs]
        images += extract_urls_from_string(post_object.content_raw, blacklist_images=False)
        images = [
            img for img in images
            if isinstance(img, str) and re.search(r"\/(?:(?!emos)\w+\.)?plurk\.com.*\.(jpg|png|gif)", img)
        ]

        artist_href = post.html.select_one(".bigplurk .avatar a")["href"]
        post.artist = Url.parse(urljoin("https://www.plurk.com/", artist_href))
        self._register_post(
            post=post,
            assets=list(dict.fromkeys(images)),
            created_at=post_object.posted,
            score=post_object.favorite_count,
        )
