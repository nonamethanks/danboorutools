from __future__ import annotations

import re
import time
from functools import cached_property
from typing import TYPE_CHECKING

import ring
from backoff import constant, on_exception
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.exceptions import MaxRetryError, ProtocolError

from danboorutools import logger
from danboorutools.exceptions import UnknownUrlError
from danboorutools.logical.sessions.poipiku import PoipikuSession
from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url, parse_list
from danboorutools.util.misc import extract_urls_from_string
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import datetime

    from backoff._typing import Details


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
        self.session.browser_get(self.normalized_url)
        assert (style := self.session.browser.find_element("css selector", "style").get_attribute("innerHTML"))
        assert (match := re.search(r"background-image: url\('(.*?)'", style))
        header_url = PoipikuHeaderImageUrl.parse_and_assert("https:" + match.groups()[0])
        return [header_url]

    def _extract_posts_from_each_page(self) -> Iterator[list[PoipikuPostUrl]]:
        page = 0
        while True:
            page_url = f"https://poipiku.com/IllustListPcV.jsp?PG={page}&ID={self.user_id}"

            self.session.browser_get(page_url)
            post_els = self.session.browser.find_elements("css selector", "#IllustThumbList .IllustThumb a.IllustInfo")
            posts_urls = parse_list([p_e.get_attribute("href") for p_e in post_els], PoipikuPostUrl)

            yield posts_urls

            page += 1

    def _process_post(self, post_object: PoipikuPostUrl) -> None:
        assets = post_object._extract_assets()
        if not assets:
            return
        self._register_post(
            post_object,
            assets=assets,
            created_at=post_object.created_at,
            score=post_object.score,
        )


DUMMY_IMGS = [
    "https://img.poipiku.com/img/publish_t_follower.png_640.jpg",
    "https://img.poipiku.com/img/R-18.png_640.jpg",
    "https://img.poipiku.com/img/warning.png_640.jpg",
    "https://img.poipiku.com/img/publish_login.png_640.jpg",
]


class MustRetryError(Exception):
    pass


def _restart_browser_on_self(params: Details) -> None:
    self: PoipikuPostUrl = params["args"][0]
    logger.debug("Browser got stuck. Restarting.")
    try:
        self.session.browser.quit()
    except TimeoutError:
        pass
    del self.session.browser
    self.session.init_browser.storage.backend.clear()


class PoipikuPostUrl(PostUrl, PoipikuUrl):
    user_id: int
    post_id: int

    normalize_template = "https://poipiku.com/{user_id}/{post_id}.html"

    @ring.lru()
    def _extract_assets(self) -> list[PoipikuImageUrl]:
        try:
            image_els = self._extract_images_from_page()
        except AssertionError as e:
            screenshot_path = self.session.browser.screenshot()
            e.add_note(f"On {self}. Screenshot: {screenshot_path}")
            raise

        try:
            return parse_list(image_els, PoipikuImageUrl)
        except UnknownUrlError as e:  # unknown dummy images
            screenshot_path = self.session.browser.screenshot()
            e.add_note(f"On {self}. Screenshot: {screenshot_path}")
            raise

    @on_exception(
        constant,
        (MustRetryError, ConnectionRefusedError, WebDriverException, MaxRetryError, ProtocolError),
        max_tries=3,
        interval=10,
        jitter=None,
        on_backoff=_restart_browser_on_self,
    )
    def _extract_images_from_page(self) -> list[str]:
        browser = self.session.browser
        if browser.current_url != self.normalized_url:
            self.session.browser_get(self.normalized_url)

        assert browser.find_elements("css selector", ".UserInfoCmdFollow.Selected")

        if browser.find_elements("css selector", ".IllustItemExpandPass"):
            logger.warning(f"Could not extract assets from {self} because of password protection.")
            return []

        expand = self._expand_images(".IllustItemExpandBtn", "ShowAppendFileF")
        image_els = WebDriverWait(browser, 10)\
            .until(ec.visibility_of_all_elements_located(("css selector", ".IllustItemThumbImg, .DetailIllustItemImage")))
        images = [i_e.get_attribute("src") for i_e in image_els]

        if images == ["https://img.poipiku.com/img/warning.png_640.jpg"] and not expand:
            # https://poipiku.com/3076546/6855175.html
            self._expand_images(".IllustItemThumb", "ShowIllustDetailF")
            image_els = WebDriverWait(browser, 10)\
                .until(ec.visibility_of_all_elements_located(("css selector", ".IllustItemThumbImg, .DetailIllustItemImage")))
            images = [i_e.get_attribute("src") for i_e in image_els]

        images = [img for img in images if img not in DUMMY_IMGS]

        if not images:
            raise MustRetryError
        return images

    def _expand_images(self, button_css: str, request_path: str) -> bool:
        browser = self.session.browser

        expand = browser.find_elements("css selector", button_css)

        if not expand:
            # logger.warning(f"Button '{button_css}' not found.")
            return False

        logger.debug(f"Clicking '{button_css}'.")
        try:
            expand[0].click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            # already clicked?
            # fuck this gay retarded site
            logger.warning(f"'{button_css}' was already clicked.")
            return False

        time.sleep(1)
        logger.debug(f"Waiting for request to '{request_path}'.")

        try:
            browser.wait_for_request(request_path, timeout=5)
        except TimeoutException:
            logger.warning(f"Request to '{request_path}' wasn't found.")

        return True

    @cached_property
    def created_at(self) -> datetime:
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
