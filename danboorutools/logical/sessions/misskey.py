from __future__ import annotations

import datetime
import os

import ring

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class MisskeySession(Session):
    @ring.lru()
    def artist_data(self, username: str) -> MisskeyUserData:
        response = self.post(
            "https://misskey.io/api/users/show",
            json={"username": username, "host": None},
            headers={"referer": "https://misskey.io/"},
        )
        return MisskeyUserData(**response.json())

    def posts(self, user_id: str, until_id: str | None = None) -> list[MisskeyPostData]:
        data = {
            "userId": user_id,
            "withRenotes": False,
            "withFiles": True,
            "withChannelNotes": True,
            "limit": 10,
        }
        if until_id:
            data["untilId"] = until_id
        response = self.post(
            "https://misskey.io/api/users/notes",
            json=data,
            headers={"referer": "https://misskey.io/"},
        )
        return [MisskeyPostData(**post) for post in response.json()]

    def feed(self, until_id: str | None = None) -> list[MisskeyPostData]:
        token = os.environ.get("MISSKEY_TOKEN")
        data = {
            "limit": 100,
            "withFiles": True,
            "withRenotes": False,
        }
        if until_id:
            data["untilId"] = until_id
        response = self.post(
            "https://misskey.art/api/notes/timeline",
            json=data,
            headers={
                "referer": "https://misskey.io/",
                "Authorization": f"Bearer {token}",
            },
        )
        return [MisskeyPostData(**post) for post in response.json()]


class MisskeyUserData(BaseModel):
    id: str
    name: str | None = None
    username: str

    url: str | None = None
    uri: str | None = None

    description: str | None = None

    @property
    def related_urls(self) -> list[Url]:
        urls = []

        if self.url:
            raise NotImplementedError(self.url, self.uri, self.description)
        if self.uri:
            raise NotImplementedError(self.url, self.uri, self.description)
        if self.description:
            urls += [Url.parse(u) for u in extract_urls_from_string(self.description)]
        return urls


class MisskeyPostData(BaseModel):
    id: str

    createdAt: datetime.datetime
    reactionCount: int
    user: MisskeyUserData

    files: list[MisskeyFileData]


class MisskeyFileData(BaseModel):
    createdAt: datetime.datetime
    url: str
