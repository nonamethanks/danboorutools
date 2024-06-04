from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url, parse_list
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class PostypeSession(Session):
    def user_data(self, username: str) -> PostypeUserData:
        user_data = self.get(f"https://api.postype.com/api/v1/channels/by/channel-name/{username}").json()
        return PostypeUserData(**user_data)


class PostypeUserData(BaseModel):
    id: int
    name: str
    bio: str

    title: str

    details: dict

    @property
    def links(self) -> list[Url]:
        links = [link["url"] for link in self.details["link"]]
        links += extract_urls_from_string(self.bio)

        return parse_list(links, Url)
