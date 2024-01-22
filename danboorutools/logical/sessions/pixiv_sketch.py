from __future__ import annotations

import os
from datetime import datetime

from pydantic import Field

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel


class PixivSketchSession(Session):
    def get_feed(self, feed_url: str) -> PixivSketchFeedData:
        feed_headers = {"x-requested-with": "https://sketch.pixiv.net/api/walls/home.json"}
        cookies = {"PHPSESSID": os.environ["PIXIV_PHPSESSID_COOKIE"]}
        feed_data = self.get(feed_url, headers=feed_headers, cookies=cookies).json()
        return PixivSketchFeedData(**feed_data)

    def user_data(self, username: str) -> PixivSketchUserData:
        cookies = {"PHPSESSID": os.environ["PIXIV_PHPSESSID_COOKIE"]}
        api_url = f"https://sketch.pixiv.net/api/users/@{username}.json"
        artist_data = self.get(api_url, cookies=cookies).json()
        return PixivSketchUserData(**artist_data["data"])

    def subscribe(self, username: str) -> None:
        user_id = self.user_data(username).id

        follow_url = f"https://sketch.pixiv.net/api/follows/{user_id}.json"
        headers = {"Referer": f"https://sketch.pixiv.net/@{username}", "x-requested-with": follow_url}

        response: dict = self.put(
            follow_url,
            headers=headers,
            data={"_k": "_v"},
            cookies={"PHPSESSID": os.environ["PIXIV_PHPSESSID_COOKIE"]},
        ).json()

        if response["data"]["following"]:
            return

        raise NotImplementedError(response)


class PixivSketchUserData(BaseModel):
    id: int
    pixiv_user_id: int
    unique_name: str
    name: str
    description: str


class PixivSketchFeedData(BaseModel):
    data: dict
    links: dict = Field(..., alias="_links")

    @property
    def posts(self) -> list[PixivSketchPostData]:
        return [PixivSketchPostData(**post) for post in self.data["items"]]

    @property
    def next_page(self) -> str:
        return "https://sketch.pixiv.net" + self.links["next"]["href"]  # pylint: disable=unsubscriptable-object


class PixivSketchPostData(BaseModel):
    id: int

    media: list[dict]

    created_at: datetime
    feedback_count: int

    user: dict
