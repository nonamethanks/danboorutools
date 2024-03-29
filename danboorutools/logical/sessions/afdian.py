from __future__ import annotations

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class AfdianSession(Session):
    def artist_data(self, username: str) -> AfdianArtistData:
        url = f"https://afdian.net/api/user/get-profile-by-slug?url_slug={username}"
        resp = self.get(url)
        data = resp.json()

        if data.get("em") == "用户不存在":  # User does not exist
            raise DeadUrlError(response=resp)

        user_data = data["data"]["user"]
        return AfdianArtistData(**user_data)


class AfdianArtistData(BaseModel):
    name: str
    creator: dict

    @property
    def related_urls(self) -> list[Url]:
        return [Url.parse(url) for url in extract_urls_from_string(self.creator["detail"])]
