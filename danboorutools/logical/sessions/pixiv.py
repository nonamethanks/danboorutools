from __future__ import annotations

import os
from datetime import datetime

from pydantic import BaseModel, Field

from danboorutools.exceptions import UrlIsDeleted
from danboorutools.logical.extractors.fanbox import FanboxArtistUrl
from danboorutools.logical.extractors.pixiv_sketch import PixivSketchArtistUrl
from danboorutools.logical.sessions import Response, Session
from danboorutools.models.url import Url

DELETION_MESSAGES = [
    "User has left pixiv or the user ID does not exist.",
    "The creator has limited who can view this content",
]


class PixivSession(Session):
    @property
    def cookies_from_env(self) -> dict:
        return {"PHPSESSID": os.environ["PIXIV_PHPSESSID_COOKIE"]}.copy()

    def get_json(self, *args, **kwargs) -> dict:
        self.cookies.clear()  # pixiv does not like it if I send it the cookies from a previous request
        resp = self.get_cached(*args, **kwargs)
        json_data = self._try_json_response(resp)

        if json_data.get("error", False) is not False:
            if json_data["message"] in DELETION_MESSAGES:
                raise UrlIsDeleted(resp)
            raise NotImplementedError(dict(json_data))

        return json_data["body"]

    def request(self, *args, **kwargs) -> Response:
        kwargs["cookies"] = self.cookies_from_env
        if "/img/" in args[1]:
            kwargs["headers"] = kwargs.get("headers", {}) | {"Referer": "https://app-api.pixiv.net/"}
        request = super().request(*args, **kwargs)
        return request

    def artist_data(self, user_id: int | str) -> PixivArtistData:
        url = f"https://www.pixiv.net/touch/ajax/user/details?id={user_id}&lang=en"
        data = self.get_json(url)["user_details"]
        return PixivArtistData(**data)

    def artist_illust_data(self, user_id: int | str, page: int) -> list[PixivArtistIllustData]:
        url = f"https://www.pixiv.net/touch/ajax/user/illusts?id={user_id}&p={page}&lang=en"
        data = self.get_json(url)["illusts"]
        return [PixivArtistIllustData(**illust_data) for illust_data in data]

    def post_data(self, post_id: int | str) -> PixivPostData:
        data = self.get_json(f"https://www.pixiv.net/ajax/illust/{post_id}?lang=en")
        return PixivPostData(**data)


class PixivArtistData(BaseModel):
    user_id: int
    user_name: str
    user_account: str
    fanbox_details: dict[str, str] | None
    social: dict[str, dict[str, str]]
    user_webpage: str | None

    @property
    def related_urls(self) -> list[Url]:
        urls = [Url.parse(url_dict["url"]) for url_dict in self.social.values()]

        if self.fanbox_details:
            urls += [FanboxArtistUrl.build(FanboxArtistUrl, username=self.fanbox_details["creator_id"])]

        sketch_url = PixivSketchArtistUrl.build(PixivSketchArtistUrl, stacc=self.user_account)
        if not sketch_url.is_deleted:
            urls += [sketch_url]

        if self.user_webpage:
            urls += [Url.parse(self.user_webpage)]

        return urls


class PixivArtistIllustData(BaseModel):
    id: int
    type: int = Field(..., gt=0, le=3)
    upload_timestamp: datetime
    rating_count: int


class PixivPostData(BaseModel):
    userId: int
    createDate: datetime  # TODO: may be worth checking uploadDate to see if it's viable to check for revisions that way
    likeCount: int
