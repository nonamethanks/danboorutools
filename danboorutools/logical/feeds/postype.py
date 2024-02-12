import os
from collections.abc import Iterator

from danboorutools.logical.urls.postype import PostypePostUrl
from danboorutools.models.feed import Feed


class PostypeFeed(Feed):
    def _extract_posts_from_each_page(self) -> Iterator[list[str]]:  # fucking patreon
        page_number = 1
        while True:
            page_url = f"https://www.postype.com/subscriptions?page={page_number}"
            page_results = self.session.get(page_url, cookies={"ps_at": os.environ["POSTYPE_PS_AT_COOKIE"]}).html
            yield [p["href"] for p in page_results.select(".component-post:not(.promotion) .post-data > a")]

            page_number += 1

    def _process_post(self, post_object: str) -> None:
        assert isinstance(post := PostypePostUrl.parse(post_object), PostypePostUrl)

        self._register_post(
            post,
            assets=post._extract_assets(),
            created_at=post.created_at,
            score=post.score,
        )

    @property
    def normalized_url(self) -> str:
        return "https://www.postype.com/subscriptions"
