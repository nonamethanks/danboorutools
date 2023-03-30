from __future__ import annotations

import os
from datetime import datetime
from functools import cached_property

import ring
from pydantic import validator
from requests_oauthlib import OAuth1

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, base36encode, extract_urls_from_string
from danboorutools.util.time import datetime_from_string


class PlurkSession(Session):
    @cached_property
    def oauth(self) -> OAuth1:
        return OAuth1(
            os.environ["PLURK_CONSUMER_KEY"],
            os.environ["PLURK_CONSUMER_SECRET"],
            os.environ["PLURK_ACCESS_TOKEN"],
            os.environ["PLURK_ACCESS_TOKEN_SECRET"],
        )

    @ring.lru()
    def user_data(self, username: str) -> PlurkArtistData:
        response = self.post("https://www.plurk.com/APP/Profile/getPublicProfile", json={"user_id": username}, auth=self.oauth)
        response_data = self._try_json_response(response)
        return PlurkArtistData(**response_data["user_info"])

    @ring.lru()
    def get_feed(self, offset: str | None = None) -> list[PlurkPostData]:
        options: dict = {"limit": 20}
        if offset:
            options["offset"] = offset

        response = self.post("https://www.plurk.com/APP/Timeline/getPlurks", json=options, auth=self.oauth)
        response_data = self._try_json_response(response)
        return [PlurkPostData(**post) for post in response_data["plurks"]]


class PlurkArtistData(BaseModel):
    id: int

    nick_name: str
    display_name: str
    full_name: str  # what's the difference?

    about: str

    @property
    def related_urls(self) -> list[Url]:
        return [Url.parse(u) for u in extract_urls_from_string(self.about)]


class PlurkPostData(BaseModel):
    plurk_id: int

    owner_id: int
    replurker_id: int | None  # really? lmao

    favorite_count: int
    posted: datetime

    content_raw: str

    @validator("posted", pre=True)
    def parse_posted(cls, value: str) -> datetime:  # pylint: disable=no-self-argument # noqa: N805 # pydantic is retarded
        return datetime_from_string(value)

    @property
    def is_repost(self) -> bool:
        return self.replurker_id and self.owner_id != self.replurker_id  # type: ignore[return-value]

    @property
    def encoded_post_id(self) -> str:
        return base36encode(self.plurk_id).lower()
