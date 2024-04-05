from __future__ import annotations

import re
from functools import cached_property
from typing import TYPE_CHECKING

from danboorutools import logger
from danboorutools.logical.sessions.fantia import FantiaPostData, FantiaSession
from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url, parse_list
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import datetime


class FantiaUrl(Url):
    session = FantiaSession()


class FantiaFanclubUrl(ArtistUrl, FantiaUrl):
    fanclub_id: int | None
    fanclub_name: str | None

    def _extract_assets(self) -> list[GalleryAssetUrl]:
        return []

    @classmethod
    def normalize(cls, **url_properties) -> str:
        if fanclub_id := url_properties["fanclub_id"]:
            return f"https://fantia.jp/fanclubs/{fanclub_id}"
        elif fanclub_name := url_properties["fanclub_name"]:
            return f"https://fantia.jp/{fanclub_name}"
        else:
            raise NotImplementedError

    @property
    def related(self) -> list[Url]:
        links = self.html.select_one(".fanclub-comment").parent.select("a")
        return [self.parse(link.attrs["href"].strip()) for link in links]

    @property
    def primary_names(self) -> list[str]:
        nickname = self.html.select_one(".single-fanclub #nickname").attrs["value"]
        assert nickname
        return [nickname]

    @property
    def secondary_names(self) -> list[str]:
        return []

    def subscribe(self) -> None:
        return self.session.subscribe(fanclub_id=self.fanclub_id)

    def unsubscribe(self) -> None:
        return self.session.unsubscribe(fanclub_id=self.fanclub_id)

    def _extract_posts_from_each_page(self) -> Iterator[list[str]]:
        return self._extract_subtype("post")

    def _extract_products_from_each_page(self) -> Iterator[list[str]]:
        return self._extract_subtype("product")

    @property
    def _extraction_methods(self):
        return [self._extract_posts_from_each_page, self._extract_products_from_each_page]

    def _extract_subtype(self, post_type: str) -> Iterator[list[str]]:
        logger.info(f"Extracting {post_type}s.")
        base_url = f"https://fantia.jp/fanclubs/{self.fanclub_id}/{post_type}s"
        page_number = 1
        while True:
            page = self.session.get(f"{base_url}?page={page_number}").html

            urls = ["https://fantia.jp" + post.attrs["href"] for post in page.select(f".{post_type} .link-block")]

            if not urls:
                break
            yield urls

            page_number += 1

    def _process_post(self, post_object: str) -> None:
        assert isinstance(post := Url.parse(post_object), FantiaPostUrl | FantiaProductUrl)
        self._register_post(
            post,
            assets=post._extract_assets(),
            created_at=post.created_at,
            score=post.score,
        )


class FantiaPostUrl(PostUrl, FantiaUrl):
    post_id: int

    normalize_template = "https://fantia.jp/posts/{post_id}"

    @cached_property
    def post_data(self) -> FantiaPostData:
        return self.session.get_post_data(self.post_id)

    def _extract_assets(self) -> list[FantiaImageUrl]:
        return parse_list(self.post_data.assets, FantiaImageUrl)

    @cached_property
    def created_at(self) -> datetime:
        return self.post_data.posted_at

    @cached_property
    def score(self) -> int:
        return self.post_data.likes_count

    @cached_property
    def gallery(self) -> FantiaFanclubUrl:
        return FantiaFanclubUrl.build(fanclub_id=self.post_data.fanclub["id"])


class FantiaProductUrl(PostUrl, FantiaUrl):
    product_id: int

    normalize_template = "https://fantia.jp/products/{product_id}"

    def _extract_assets(self) -> list[FantiaImageUrl]:
        img_els = self.html.select(".product-gallery img")
        assert img_els, self.normalized_url
        return parse_list([img_el.attrs["src"] for img_el in img_els], FantiaImageUrl)

    @cached_property
    def created_at(self) -> None:
        return self._extract_assets()[0].created_at

    @cached_property
    def score(self) -> int:
        return 0

    @cached_property
    def gallery(self) -> FantiaFanclubUrl:
        assert (href := self.html.select_one(".fanclub-name a"))
        artist_url = "https://fantia.jp" + href.attrs["href"]
        assert isinstance(parsed_url := FantiaFanclubUrl.parse(artist_url), FantiaFanclubUrl)
        return parsed_url


class FantiaFanclubAssetUrl(GalleryAssetUrl, FantiaUrl):
    fanclub_id: int

    @property
    def full_size(self) -> str:
        return re.sub(r"(\d+\/)(\w+_)+", r"\1", self.parsed_url.raw_url).replace(".webp", ".jpg")


class FantiaImageUrl(PostAssetUrl, FantiaUrl):
    image_id: int
    image_type: str | None
    post_id: int | None
    image_uuid: str | None
    # could also be downloadable

    @property
    def full_size(self) -> str:
        if self.image_type == "post":
            assert self.post_id
            assert self.image_uuid
            return f"https://c.fantia.jp/uploads/post/file/{self.post_id}/{self.image_uuid}.{self.parsed_url.extension}"
        elif self.image_type == "product":
            assert self.post_id
            assert self.image_uuid
            return f"https://c.fantia.jp/uploads/product/image/{self.post_id}/{self.image_uuid}.{self.parsed_url.extension}"
        elif self.image_type == "product_image":
            assert self.image_uuid
            return f"https://c.fantia.jp/uploads/product_image/file/{self.image_id}/{self.image_uuid}.{self.parsed_url.extension}"
        else:
            return self.parsed_url.raw_url
            # FIXME: is it correct in case of https://fantia.jp/posts/343039/post_content_photo/1617547? Probably not. hmmm

    @property
    def _unique_url_for_hash(self) -> str:
        return self.parsed_url.url_without_query

    @property
    def created_at(self) -> datetime:
        last_modified = self.session.head(self.full_size).headers["Last-Modified"]
        return datetime_from_string(last_modified)
