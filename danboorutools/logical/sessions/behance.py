from __future__ import annotations

import ring

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel


class BehanceSession(Session):
    @ring.lru()
    def user_data(self, username: str) -> BehanceUserData:
        headers = {"x-requested-with": "XMLHttpRequest"}
        user_data = self.get_json(f"https://www.behance.net/{username}/projects", headers=headers)
        return BehanceUserData(**user_data["profile"]["owner"])


class BehanceUserData(BaseModel):
    id: int
    display_name: str

    website: str

    links: list

    social_links: list[dict[str, str]]

    @property
    def related_urls(self) -> list[Url]:
        urls: list[Url] = []

        if self.links:
            raise NotImplementedError(self.links)

        if self.website:
            urls.append(Url.parse(self.website))

        for link in self.social_links:
            urls += [Url.parse(link["url"])]

        return urls
