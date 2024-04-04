from collections.abc import Iterator

from danboorutools import logger
from danboorutools.logical.sessions.fantia import FantiaSession
from danboorutools.logical.urls.fantia import FantiaPostUrl, FantiaProductUrl
from danboorutools.models.feed import Feed


class FantiaFeed(Feed):
    session = FantiaSession()

    def _extract_posts_from_each_page(self) -> Iterator[list[FantiaPostUrl]]:
        self.first_page_must_have_posts = True
        return self._extract_subtype("post")

    def _extract_products_from_each_page(self) -> Iterator[list[FantiaProductUrl]]:
        self.first_page_must_have_posts = False
        return self._extract_subtype("product")

    @property
    def _extraction_methods(self):
        return [self._extract_posts_from_each_page, self._extract_products_from_each_page]

    def _extract_subtype(self, subtype: str) -> Iterator[list[FantiaPostUrl | FantiaProductUrl]]:
        logger.info(f"Extracting {subtype}s.")
        page = 1
        while True:
            page_json = self.session.get_feed(page=page, content_type=f"{subtype}s")

            if subtype == "post":
                urls = [FantiaPostUrl.build(post_id=post_object["id"]) for post_object in page_json["posts"]]
            elif subtype == "product":
                urls = [FantiaProductUrl.build(product_id=post_object["id"]) for post_object in page_json["products"]]
            else:
                raise NotImplementedError(subtype)
            yield urls

            if not page_json["has_next"]:
                return

    def _process_post(self, post_object: FantiaPostUrl | FantiaProductUrl) -> None:

        self._register_post(
            post=post_object,
            assets=post_object._extract_assets(),
            score=post_object.score,
            created_at=post_object.created_at,
        )

    @property
    def normalized_url(self) -> str:
        return "https://fantia.jp/mypage/posts"
