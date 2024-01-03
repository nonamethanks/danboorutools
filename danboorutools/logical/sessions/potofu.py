from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel


class PotofuSession(Session):
    def user_data(self, user_id: str) -> PotofuArtistData:
        user_data = self.get(f"https://api.potofu.me/users/{user_id}").json()
        return PotofuArtistData(**user_data["user"])


class PotofuArtistData(BaseModel):
    name: str
    name_en: str

    links: list[dict]

    @property
    def related_urls(self) -> list[Url]:
        if not self.links:
            raise NotImplementedError(self)
        return [Url.parse(link["url"]) for link in self.links]
