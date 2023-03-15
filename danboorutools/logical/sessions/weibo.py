from __future__ import annotations

import os
from typing import TYPE_CHECKING

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string

if TYPE_CHECKING:
    from requests import Response


class WeiboSession(Session):
    weibo_sub_cookie = os.environ["WEIBO_SUB_COOKIE"]
    weibo_wbpsess = os.environ["WEIBO_WBPSESS_COOKIE"]

    def request(self, *args, **kwargs) -> Response:
        cookies = {"SUB": self.weibo_sub_cookie, "WBPSESS": self.weibo_wbpsess}
        kwargs["cookies"] = kwargs.get("cookies", {}) | cookies
        return super().request(*args, **kwargs)

    def user_data(self,
                  short_id: int | None = None,
                  long_id: int | None = None,
                  username: str | None = None,
                  screen_name: str | None = None,
                  ) -> WeiboUserData:
        if short_id:
            data = self.get(f"https://www.weibo.com/ajax/profile/info?uid={short_id}").json()
        elif long_id or username:
            data = self.get(f"https://www.weibo.com/ajax/profile/info?custom={long_id or username}").json()
        elif screen_name:
            data = self.get(f"https://www.weibo.com/ajax/profile/info?screen_name={screen_name}").json()
        else:
            raise NotImplementedError

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
