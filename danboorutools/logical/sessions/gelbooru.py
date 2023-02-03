import os

import regex
from requests import Response

from danboorutools import logger
from danboorutools.logical.sessions import Session
from danboorutools.models.gelbooru import GelbooruPost
from danboorutools.version import version


class GelbooruApi(Session):
    base_url = "https://gelbooru.com"

    csrf_pattern = regex.compile(r'name="csrf-token" value="(\w+)"/>')

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.config_user_id = os.environ["GELBOORU_USER_ID"]
        self.config_username = os.environ["GELBOORU_USERNAME"]
        self.auth = (self.config_user_id, os.environ["GELBOORU_API_KEY"])

    def gelbooru_request(self, method: str, endpoint: str, *args, **kwargs) -> Response:
        kwargs["headers"] = {"User-Agent": f"DanbooruTools/{version}"}
        if kwargs.get("params", {}).get("json") == 1:
            kwargs["Content-Type"] = "application/json"

        endpoint_url = self.base_url.strip("/") + "/" + endpoint.strip("/")
        response = self.request(method, endpoint_url, *args, **kwargs)
        logger.debug(f"{method} request made to {response.url}")
        assert response.ok

        return response

    def posts(self, tags: list[str] | None = None) -> list[GelbooruPost]:
        params = {
            "page": "dapi",
            "s": "post",
            "q": "index",
            "json": 1,
            "pid": 0,  # page number
            "limit": 100,
            "tags": " ".join(tags) if tags else "",
        }

        data = self.gelbooru_request("GET", "index.php", params=params).json()
        return [GelbooruPost(post_data) for post_data in data["post"]]

    def get_csrf(self, response: Response) -> str:
        match = self.csrf_pattern.search(response.text)
        assert match
        return match.group(1)
