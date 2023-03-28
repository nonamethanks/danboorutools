from __future__ import annotations

import ring

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class NicovideoSession(Session):
    @ring.lru()
    def nicoseiga_artist_data(self, user_id: int) -> NicoseigaArtistData:
        url = f"https://nvapi.nicovideo.jp/v1/users/{user_id}"
        headers = {"X-Frontend-Id": "3"}
        response = self.get_json(url, headers=headers)["data"]["user"]
        return NicoseigaArtistData(**response)


class NicoseigaArtistData(BaseModel):
    id: int
    nickname: str
    description: str

    @property
    def related_urls(self) -> list[Url]:
        return [Url.parse(u) for u in extract_urls_from_string(self.description)]
