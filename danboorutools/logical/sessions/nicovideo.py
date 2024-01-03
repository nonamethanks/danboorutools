from __future__ import annotations

import os
from datetime import datetime

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class NicovideoSession(Session):
    def nicovideo_artist_data(self, user_id: int) -> NicoSeigaArtistData:
        url = f"https://nvapi.nicovideo.jp/v1/users/{user_id}"
        headers = {"X-Frontend-Id": "3"}
        response = self.get(url, headers=headers).json()["data"]["user"]
        return NicoSeigaArtistData(**response)

    def get_nicoseiga_feed(self, min_id: int | None = None) -> NicoSeigaFeedData:
        page_url = "https://public.api.nicovideo.jp/v1/timelines/nicorepo/last-1-month/my/pc/entries.json"
        if min_id:
            page_url += f"?untilId={min_id}"
        page_json = self.get(page_url, cookies={"user_session": os.environ["NICOSEIGA_USER_SESSION_COOKIE"]}).json()
        return NicoSeigaFeedData(**page_json)


class NicoSeigaArtistData(BaseModel):
    id: int
    nickname: str
    description: str

    @property
    def related_urls(self) -> list[Url]:
        from danboorutools.logical.urls.nicovideo import NicovideoCommunityUrl

        return [
            parsed_url
            for parsed_url in map(Url.parse, extract_urls_from_string(self.description))
            if not isinstance(parsed_url, NicovideoCommunityUrl)
        ]


class NicoSeigaPostData(BaseModel):
    id: str
    object: dict
    updated: datetime
    muteContext: dict


class NicoSeigaFeedData(BaseModel):
    data: list[NicoSeigaPostData]
    meta: dict
