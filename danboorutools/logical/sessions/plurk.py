from __future__ import annotations

import os
from functools import cached_property

from requests_oauthlib import OAuth1

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string, memoize


class PlurkSession(Session):
    @cached_property
    def oauth(self) -> OAuth1:
        return OAuth1(
            os.environ["PLURK_CONSUMER_KEY"],
            os.environ["PLURK_CONSUMER_SECRET"],
            os.environ["PLURK_ACCESS_TOKEN"],
            os.environ["PLURK_ACCESS_TOKEN_SECRET"],
        )

    @memoize
    def user_data(self, username: str) -> PlurkArtistData:
        response = self.post("https://www.plurk.com/APP/Profile/getPublicProfile", json={"user_id": username}, auth=self.oauth)
        response_data = self._try_json_response(response)
        return PlurkArtistData(**response_data["user_info"])


class PlurkArtistData(BaseModel):
    id: int

    nick_name: str
    display_name: str
    full_name: str  # what's the difference?

    about: str

    @property
    def related_urls(self) -> list[Url]:
        return [Url.parse(u) for u in extract_urls_from_string(self.about)]
