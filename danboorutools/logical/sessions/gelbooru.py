import os
import re
import time

from requests import Response

from danboorutools import logger
from danboorutools.logical.sessions import Session
from danboorutools.models.gelbooru import GelbooruPost
from danboorutools.util.misc import memoize
from danboorutools.version import version


class GelbooruApi(Session):
    base_url = "https://gelbooru.com"

    csrf_pattern = re.compile(r'name="csrf-token" value="(\w+)"/>')

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.config_user_id = os.environ["GELBOORU_USER_ID"]
        self.config_username = os.environ["GELBOORU_USERNAME"]
        self.config_password = os.environ["GELBOORU_PASSWORD"]
        self.auth = (self.config_user_id, os.environ["GELBOORU_API_KEY"])

    @memoize
    def login(self) -> None:
        data = {
            "user": self.config_username,
            "pass": self.config_password,
            "submit": "Log in"
        }
        response = self.gelbooru_request("POST", "/index.php?page=account&s=login&code=00", data=data)
        assert response.ok

    def gelbooru_request(self, method: str, endpoint: str, *args, **kwargs) -> Response:
        kwargs["headers"] = {"User-Agent": f"DanbooruTools/{version}"}
        if kwargs.get("params", {}).get("json") == 1:
            kwargs["headers"]["Content-Type"] = "application/json"

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
        if not data.get("post") and data["@attributes"]["count"] == 0:
            return []
        else:
            return [GelbooruPost(post_data) for post_data in data["post"]]

    def get_csrf(self, response: Response) -> str:
        match = self.csrf_pattern.search(response.text)
        assert match
        return match.group(1)

    def update(self, post: GelbooruPost, tags: list[str], rating: str | None = None) -> None:
        self.login()

        final_tags = post.tags + [t for t in tags if not t.startswith("-")]
        final_tags = [t for t in final_tags if f"-{t}" not in tags]

        first_request = self.gelbooru_request("GET", f"/index.php?page=post&s=view&id={post.id}")
        token = self.get_csrf(first_request)

        payload: dict[str, int | str] = {
            "csrf-token": token,
            "id": post.id,
            "lupdated": int(time.time()),
            "pconf": 1,
            "rating": rating[0] if rating else post.rating,
            "source": post.source.original_url,
            "submit": "Save changes",
            "tags": " ".join(final_tags),
            "title": "",
            "uid": self.config_user_id,
            "uname": self.config_username,
        }

        if ">Unlock Image</a>" in first_request.text:
            self.unlock(post, token)

        self.gelbooru_request("POST", "/public/edit_post.php", data=payload)

    def unlock(self, post: GelbooruPost, token: str) -> None:
        lock_url = f"/public/lock.php?id={post.id}&csrf-token={token}"
        self.gelbooru_request("GET", lock_url)


gelbooru_api = GelbooruApi()
