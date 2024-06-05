from __future__ import annotations

import json

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url, parse_list
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class PostypeSession(Session):
    def user_data(self, username: str) -> PostypeUserData:
        user_data = self.get(f"https://api.postype.com/api/v1/channels/by/channel-name/{username}").json()
        return PostypeUserData(**user_data)

    def user_posts(self, username: str, page: int = 1) -> list[PostypePostData]:
        url = f"https://www.postype.com/@{username}/post?page={page}&sortType=RECENT&_rsc=9tx0r"

        response = self.get(url, headers={"Referer": f"https://www.postype.com/@{username}/post", "rsc": "1"})
        raw_data = [k for k in response.text.strip().split("\n") if "posty.pe" in k]
        assert len(raw_data) == 1, raw_data
        parsed_data = json.loads(raw_data[0][3:])[-1]["children"][-1]["children"][1][-1]["children"]

        return [PostypePostData(**child[-1]["children"][-1]) for child in parsed_data]


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


class PostypePostData(BaseModel):
    id: int
    title: str
    channelName: str

    shortUrl: str
