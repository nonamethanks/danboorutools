from __future__ import annotations

import os
from json import JSONDecodeError
from typing import TYPE_CHECKING

from danboorutools.exceptions import DeadUrlError, NotLoggedInError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string

if TYPE_CHECKING:
    from requests import Response


class WeiboSession(Session):
    weibo_sub_cookie = os.environ["WEIBO_SUB_COOKIE"]
    # weibo_wbpsess = os.environ["WEIBO_WBPSESS_COOKIE"]

    def request(self, *args, **kwargs) -> Response:
        cookies = {"SUB": self.weibo_sub_cookie}
        kwargs["cookies"] = kwargs.get("cookies", {}) | cookies
        return super().request(*args, **kwargs)

    def user_data(self,
                  short_id: int | None = None,
                  long_id: int | None = None,
                  username: str | None = None,
                  screen_name: str | None = None,
                  ) -> WeiboUserData:
        if short_id:
            data_url = f"https://weibo.com/ajax/profile/info?uid={short_id}"
        elif long_id or username:
            data_url = f"https://weibo.com/ajax/profile/info?custom={long_id or username}"
        elif screen_name:
            data_url = f"https://weibo.com/ajax/profile/info?screen_name={screen_name}"
        else:
            raise NotImplementedError

        response = self.get(data_url, headers={"Accept": "application/json, text/plain, */*"})

        if not response.ok:
            raise NotImplementedError(response, data_url, response.content)

        try:
            data = response.json()
        except JSONDecodeError as e:
            if "weibo.com/signup/signup.php" in response.url:
                raise NotLoggedInError(response, original_url=data_url) from e
            raise NotImplementedError(data_url, response.url) from e

        if data.get("msg") == "该用户不存在(20003)":  # user does not exist
            raise DeadUrlError(response)

        return WeiboUserData(**data["data"]["user"])


class WeiboUserData(BaseModel):
    id: int
    screen_name: str
    domain: str

    url: str
    description: str

    @property
    def related_urls(self) -> list[Url]:
        urls = [Url.parse(u) for u in extract_urls_from_string(self.description)]

        if self.url:
            urls += [Url.parse(self.url)]

        return list(dict.fromkeys(urls))
