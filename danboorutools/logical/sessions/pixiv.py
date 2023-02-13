import json
import os
from functools import cached_property

from danboorutools.exceptions import HTTPError, UrlIsDeleted
from danboorutools.logical.sessions import Session
from danboorutools.util.misc import memoize


class PixivSession(Session):
    @cached_property
    def cookies_from_env(self) -> dict:
        return {"PHPSESSID": os.environ["PIXIV_PHPSESSID_COOKIE"]}

    @memoize
    def get_json(self, url: str) -> dict:
        resp = self.get(url, cookies=self.cookies_from_env)
        try:
            json_data: dict = resp.json()
        except json.JSONDecodeError as e:
            print(resp.text)
            raise HTTPError(resp) from e

        if json_data.get("error", False) is not False:
            if json_data["message"] == "The creator has limited who can view this content":
                raise UrlIsDeleted(resp)
            raise NotImplementedError(dict(json_data))

        return json_data["body"]

    def download_file(self, *args, **kwargs):  # noqa
        headers = {"Referer": "https://app-api.pixiv.net/"}
        return super().download_file(*args, headers=headers, **kwargs)
