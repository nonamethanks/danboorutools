from __future__ import annotations

import os
from datetime import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import Field

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.fanbox import FanboxArtistUrl
from danboorutools.logical.urls.pixiv_sketch import PixivSketchArtistUrl
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel

if TYPE_CHECKING:
    from requests import Response


DELETION_MESSAGES = [
    "User has left pixiv or the user ID does not exist.",
    "The creator has limited who can view this content",
]


class PixivSession(Session):
    @property
    def cookies_from_env(self) -> dict[str, str]:
        return {"PHPSESSID": os.environ["PIXIV_PHPSESSID_COOKIE"]}.copy()

    def get_json(self, *args, skip_cache: bool = False, **kwargs) -> dict:
        self.cookies.clear()  # pixiv does not like it if I send it the cookies from a previous request
        resp = self.get(*args, skip_cache=skip_cache, **kwargs)
        json_data = self._try_json_response(resp)

        if json_data.get("error", False) is not False:
            if json_data["message"] in DELETION_MESSAGES:
                raise DeadUrlError(resp)
            raise NotImplementedError(dict(json_data))

        return json_data["body"]

    def request(self, *args, **kwargs) -> Response:
        kwargs["cookies"] = self.cookies_from_env
        if "/img/" in args[1]:
            kwargs["headers"] = kwargs.get("headers", {}) | {"Referer": "https://app-api.pixiv.net/"}
        return super().request(*args, **kwargs)

    def artist_data(self, user_id: int | str) -> PixivArtistData:
        url = f"https://www.pixiv.net/touch/ajax/user/details?id={user_id}&lang=en"
        data = self.get_json(url)
        return PixivArtistData(**data["user_details"])

    def post_data(self, post_id: int | str) -> PixivSingleIllustData:
        data = self.get_json(f"https://www.pixiv.net/ajax/illust/{post_id}?lang=en")
        return PixivSingleIllustData(**data)

    def get_feed(self, page: int) -> list[PixivGroupedIllustData]:
        url = f"https://www.pixiv.net/touch/ajax/follow/latest?type=illusts&include_meta=0&p={page}&lang=en"
        json_data = self.get_json(url)
        if not (posts_data := json_data["illusts"]):
            raise NotImplementedError("No posts found. Check cookie.")
        return [PixivGroupedIllustData(**post_data) for post_data in posts_data]

    def get_user_illusts(self, user_id: int, page: int) -> list[PixivGroupedIllustData]:
        url = f"https://www.pixiv.net/touch/ajax/user/illusts?id={user_id}&p={page}&lang=en"
        json_data = self.get_json(url)
        return [PixivGroupedIllustData(**post_data) for post_data in json_data["body"]["illusts"]]


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

    rating_count: int | None  # the feed endpoint doesn't have it


class PixivSingleIllustData(BaseModel):
    id: int
    userId: int

    createDate: datetime  # TODO: may be worth checking uploadDate to see if it's viable to check for revisions that way

    likeCount: int
