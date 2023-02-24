import json
import os

from danboorutools.exceptions import HTTPError, UrlIsDeleted
from danboorutools.logical.sessions import Response, Session
from danboorutools.util.misc import memoize

DELETION_MESSAGES = [
    "User has left pixiv or the user ID does not exist.",
    "The creator has limited who can view this content",
]


class PixivSession(Session):
    @property
    def cookies_from_env(self) -> dict:
        return {"PHPSESSID": os.environ["PIXIV_PHPSESSID_COOKIE"]}.copy()

    @memoize
    def get_json(self, url: str) -> dict:
        self.cookies.clear()  # pixiv does not like it if I send it the cookies from a previous request
        resp = self.get(url, cookies=self.cookies_from_env)
        try:
            json_data: dict = resp.json()
        except json.JSONDecodeError as e:
            print(resp.text)
            raise HTTPError(resp) from e

        if json_data.get("error", False) is not False:
            if json_data["message"] in DELETION_MESSAGES:
                raise UrlIsDeleted(resp)
            raise NotImplementedError(dict(json_data))

        return json_data["body"]

    def request(self, *args, **kwargs) -> Response:
        kwargs["cookies"] = self.cookies_from_env
        return super().request(*args, **kwargs)

    def download_file(self, *args, **kwargs):  # noqa
        headers = {"Referer": "https://app-api.pixiv.net/"}
        return super().download_file(*args, headers=headers, **kwargs)
