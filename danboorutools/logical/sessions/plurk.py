from __future__ import annotations

import os
from functools import cached_property

from plurk_oauth import PlurkAPI

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string, memoize


class PlurkSession(Session):
    @cached_property
    def api(self) -> PlurkAPI:
        api = PlurkAPI(os.environ["PLURK_CONSUMER_KEY"], os.environ["PLURK_CONSUMER_SECRET"])
        api.authorize(os.environ["PLURK_ACCESS_TOKEN"], os.environ["PLURK_ACCESS_TOKEN_SECRET"])
        return api

    @memoize
    def user_data(self, username: str) -> PlurkArtistData:
        response = self.api.callAPI("/APP/Profile/getPublicProfile", options={"user_id": username})
        return PlurkArtistData(**response["user_info"])


class PlurkArtistData(BaseModel):
    id: int

    nick_name: str
    display_name: str
    full_name: str  # what's the difference?

    about: str

    @property
    def related_urls(self) -> list[Url]:
        return [Url.parse(u) for u in extract_urls_from_string(self.about)]
