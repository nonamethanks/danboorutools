from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Literal

import ring
from pydantic import Field

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions import ScraperResponse, Session
from danboorutools.logical.urls.fanbox import FanboxArtistUrl
from danboorutools.logical.urls.pixiv_sketch import PixivSketchArtistUrl
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel

DELETION_MESSAGES = [
    "User has left pixiv or the user ID does not exist.",
    "The creator has limited who can view this content",
    "Profile not found",
]


class PixivSession(Session):
    def get_api(self, url: str) -> dict:
        self.cookies.clear()  # pixiv does not like it if I send it the cookies from a previous request
        resp = self.get(url)
        json_data = resp.json()

        if json_data.get("error", False) is not False:
            if json_data["message"] in DELETION_MESSAGES:
                raise DeadUrlError(resp)
            raise NotImplementedError(dict(json_data))

        return json_data["body"]

    def request(self, *args, **kwargs) -> ScraperResponse:
        kwargs["cookies"] = {"PHPSESSID": os.environ["PIXIV_PHPSESSID_COOKIE"]}
        if "/img/" in args[1]:
            kwargs["headers"] = kwargs.get("headers", {}) | {"Referer": "https://app-api.pixiv.net/"}
        return super().request(*args, **kwargs)

    def artist_data(self, user_id: int | str) -> PixivArtistData:
        url = f"https://www.pixiv.net/touch/ajax/user/details?id={user_id}&lang=en"
        data = self.get_api(url)
        return PixivArtistData(**data["user_details"])

    def post_data(self, post_id: int | str) -> PixivSingleIllustData:
        data = self.get_api(f"https://www.pixiv.net/ajax/illust/{post_id}?lang=en")
        return PixivSingleIllustData(**data)

    def get_feed(self, page: int) -> list[PixivGroupedIllustData]:
        url = f"https://www.pixiv.net/touch/ajax/follow/latest?type=illusts&include_meta=0&p={page}&lang=en"
        json_data = self.get_api(url)
        if not (posts_data := json_data["illusts"]):
            raise NotImplementedError("No posts found. Check cookie.")
        return [PixivGroupedIllustData(**post_data) for post_data in posts_data]

    def get_user_illusts(self, user_id: int, page: int) -> list[PixivGroupedIllustData]:
        url = f"https://www.pixiv.net/touch/ajax/user/illusts?id={user_id}&p={page}&lang=en"
        json_data = self.get_api(url)
        illusts = json_data["illusts"]
        return [PixivGroupedIllustData(**post_data) for post_data in illusts]

    def subscribe(self, user_id: int) -> None:
        self.browser_login()

        self.browser.get(f"https://www.pixiv.net/en/users/{user_id}")
        button = self.browser.find_element("css selector", "button[data-click-label='follow']")
        if button.text.strip() == "Following":
            return

        button.click()
        attempts = 0
        while attempts < 5:
            button = self.browser.find_element("css selector", "button[data-click-label='follow']")
            if button.text.strip() == "Following":
                return

            attempts += 1
            time.sleep(1)

        raise NotImplementedError(button.text)

    @ring.lru()
    def browser_login(self) -> None:
        self.browser.delete_all_cookies()
        cookie = {"name": "PHPSESSID", "value": os.environ["PIXIV_PHPSESSID_COOKIE"], "domain": ".pixiv.net"}
        self.browser.execute_cdp_cmd("Network.enable", {})
        self.browser.execute_cdp_cmd("Network.setCookie", cookie)
        self.browser.execute_cdp_cmd("Network.disable", {})

        # self.browser.get("https://www.pixiv.net/dashboard")
        # if not self.browser.find_elements_by_text("Try posting your work"):
        #     screenshot_path = self.browser.screenshot()
        #     raise NotImplementedError(f"Could not log in. See {screenshot_path}")


class PixivArtistData(BaseModel):
    user_id: int
    user_name: str
    user_account: str
    fanbox_details: dict[str, str | Literal[False]] | None   # cover_image_url can be false
    social: dict[str, dict[str, str]] | list
    user_webpage: str | None

    @property
    def related_urls(self) -> list[Url]:
        if isinstance(self.social, list):
            urls = []
            if self.social:
                raise NotImplementedError(self.social)  # I assume it can only be a list if it's empty, otherwise they changed something
        else:
            urls = [Url.parse(url_dict["url"]) for url_dict in self.social.values()]

        if self.fanbox_details:
            urls += [FanboxArtistUrl.build(username=self.fanbox_details["creator_id"])]

        sketch_url = PixivSketchArtistUrl.build(stacc=self.user_account)
        if not sketch_url.is_deleted:
            urls += [sketch_url]

        if self.user_webpage:
            urls += [Url.parse(self.user_webpage)]

        return urls


class PixivGroupedIllustData(BaseModel):
    id: int
    user_id: int
    type: int = Field(..., ge=0, lt=3)

    upload_timestamp: datetime

    # rating_count: int | None  # the feed endpoint doesn't have it


class PixivSingleIllustData(BaseModel):
    id: int
    userId: int

    createDate: datetime  # TODO: may be worth checking uploadDate to see if it's viable to check for revisions that way

    likeCount: int
