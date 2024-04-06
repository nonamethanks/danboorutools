from __future__ import annotations

import re
import time
from functools import cached_property
from typing import TYPE_CHECKING

from danboorutools.logical.sessions.poipiku import PoipikuSession
from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url, parse_list
from danboorutools.util.misc import extract_urls_from_string
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import datetime


class PoipikuUrl(Url):
    session = PoipikuSession()


class PoipikuArtistUrl(ArtistUrl, PoipikuUrl):
    user_id: int

    normalize_template = "https://poipiku.com/{user_id}/"

    @property
    def primary_names(self) -> list[str]:
        assert (name_el := self.html.select_one(".UserInfoUserName"))
        return [name_el.text]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        user_profile = str(self.html.select_one(".UserInfoProfile"))
        return [Url.parse(u) for u in extract_urls_from_string(user_profile)]

    def subscribe(self) -> None:
        self.session.subscribe(self.user_id)

    def unsubscribe(self) -> None:
        self.session.unsubscribe(self.user_id)

    def _extract_assets(self) -> list[PoipikuHeaderImageUrl]:
        self.session.init_browser()
        self.session.browser.get(self.normalized_url)
        assert (style := self.session.browser.find_element("css selector", "style").get_attribute("innerHTML"))
        assert (match := re.search(r"background-image: url\('(.*?)'", style))
        header_url = self.parse("https:" + match.groups()[0])
        assert isinstance(header_url, PoipikuHeaderImageUrl), header_url
        return [header_url]

    def _extract_posts_from_each_page(self) -> Iterator[list[PoipikuPostUrl]]:
        page = 0
        self.session.init_browser()
        while True:
            page_url = f"https://poipiku.com/IllustListPcV.jsp?PG={page}&ID={self.user_id}"

            self.session.browser.get(page_url)
            post_els = self.session.browser.find_elements("css selector", "#IllustThumbList .IllustThumb a.IllustInfo")
            posts_urls = parse_list([p_e.get_attribute("href") for p_e in post_els], PoipikuPostUrl)

            yield posts_urls

            page += 1

    def _process_post(self, post_object: PoipikuPostUrl) -> None:
        self._register_post(
            post_object,
            assets=post_object._extract_assets(),
            created_at=post_object.created_at,
            score=post_object.score,
        )


DUMMY_IMGS = [
    "https://img.poipiku.com/img/R-18.png_640.jpg",
    "https://img.poipiku.com/img/publish_t_follower.png_640.jpg",
]


class PoipikuPostUrl(PostUrl, PoipikuUrl):
    user_id: int
    post_id: int

    normalize_template = "https://poipiku.com/{user_id}/{post_id}.html"

    def _extract_assets(self) -> list[PoipikuImageUrl]:
        self.session.init_browser()
        browser = self.session.browser
        if browser.current_url != self.normalized_url:
            browser.get(self.normalized_url)
        if (expand := browser.find_elements("css selector", ".IllustItemExpandBtn")):
            expand[0].click()
            browser.wait_for_request("ShowAppendFileF")
            time.sleep(1)

        image_els = [
            i_e.get_attribute("src") for i_e in
            browser.find_elements("css selector", ".IllustItemThumbImg")
        ]

        image_els = [
            img for img in image_els
            if img not in DUMMY_IMGS
        ]
        assert image_els

        return parse_list(image_els, PoipikuImageUrl)

    @cached_property
    def created_at(self) -> str:
        return self._extract_assets()[0].created_at

    @cached_property
    def score(self) -> int:
        return 0

    @cached_property
    def gallery(self) -> PoipikuArtistUrl:
        return PoipikuArtistUrl.build(user_id=self.user_id)


class PoipikuHeaderImageUrl(GalleryAssetUrl, PoipikuUrl):
    user_id: int
    image_hash: str
    image_id: int

    @property
    def full_size(self) -> str:
        original_url = re.sub(r"(\.\w+)_\d+\.\w+$", "\\1", self.parsed_url.raw_url)
        return original_url

    @cached_property
    def gallery(self) -> PoipikuArtistUrl:
        return PoipikuArtistUrl.build(user_id=self.user_id)


class PoipikuImageUrl(PostAssetUrl, PoipikuUrl):
    user_id: int
    post_id: int
    image_hash: str | None
    image_id: int | None

    @property
    def full_size(self) -> str:
        original_url = re.sub(r"(\.\w+)_\d+\.\w+$", "\\1", self.parsed_url.raw_url)
        return original_url

    @cached_property
    def created_at(self) -> datetime:
        last_modified = self.session.head(self.full_size).headers["Last-Modified"]
        return datetime_from_string(last_modified)

    @cached_property
    def post(self) -> PoipikuPostUrl:
        return PoipikuPostUrl.build(user_id=self.user_id, post_id=self.post_id)
