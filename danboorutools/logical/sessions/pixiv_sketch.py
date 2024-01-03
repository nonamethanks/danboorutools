from __future__ import annotations

from datetime import datetime

from pydantic import Field

from danboorutools.logical.sessions import Session
from danboorutools.logical.sessions.pixiv import PixivSession
from danboorutools.util.misc import BaseModel


class PixivSketchSession(Session):
    def get_feed(self, feed_url: str) -> PixivSketchFeedData:
        feed_headers = {"x-requested-with": "https://sketch.pixiv.net/api/walls/home.json"}
        feed_data = self.get(feed_url, headers=feed_headers, cookies=PixivSession().cookies_from_env).json()
        return PixivSketchFeedData(**feed_data)


class PixivSketchFeedData(BaseModel):
    data: dict
    links: dict = Field(..., alias="_links")

    @property
    def posts(self) -> list[PixivSketchPostData]:
        return [PixivSketchPostData(**post) for post in self.data["items"]]

    @property
    def next_page(self) -> str:
        return "https://sketch.pixiv.net" + self.links["next"]["href"]


class PixivSketchPostData(BaseModel):
    id: int

    media: list[dict]

    created_at: datetime
    feedback_count: int

    user: dict
