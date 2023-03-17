from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, memoize


class MisskeySession(Session):
    @memoize
    def artist_data(self, username: str) -> MisskeyUserData:
        response = self.post(
            "https://misskey.io/api/users/show",
            json={"username": username, "host": None},
            headers={"referer": "https://misskey.io/"},
        )
        data = self._try_json_response(response)
        return MisskeyUserData(**data)


class MisskeyUserData(BaseModel):
    id: str
    name: str | None
    username: str

    url: str | None
    uri: str | None

    description: str | None

    @property
    def related_urls(self) -> list[Url]:
        if self.url:
            raise NotImplementedError(self.url, self.uri, self.description)
        if self.uri:
            raise NotImplementedError(self.url, self.uri, self.description)
        if self.description:
            raise NotImplementedError(self.url, self.uri, self.description)
        return []
