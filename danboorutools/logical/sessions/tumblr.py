from __future__ import annotations

import os
import re
from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from requests_oauthlib import OAuth1

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string

if TYPE_CHECKING:
    from danboorutools.models.file import FileSubclass


class TumblrSession(Session):
    @cached_property
    def oauth(self) -> OAuth1:
        return OAuth1(
            os.environ["TUMBLR_CONSUMER_KEY"],
            os.environ["TUMBLR_CONSUMER_SECRET"],
            os.environ["TUMBLR_ACCESS_TOKEN"],
            os.environ["TUMBLR_ACCESS_TOKEN_SECRET"],
        )

    def _validate_api_response(self, response: dict) -> dict:
        assert response["meta"]["status"] == 200, response
        return response["response"]

    def api_request(self, method: str, path: str, *args, **kwargs) -> dict:
        url = f"https://api.tumblr.com/v2/{path.strip("/")}"

        try:
            response = self.request(method, url, *args, auth=self.oauth, **kwargs).json()
        except DeadUrlError as e:
            e.add_note(e.response.content)
            raise

        assert response["meta"]["status"] == 200, response
        return response["response"]

    def blog_data(self, blog_name: str) -> TumblrBlogData:
        response = self.api_request("GET", f"blog/{blog_name}/info")
        return TumblrBlogData(**response["blog"])

    def get_feed(self, offset: int = 0) -> list[TumblrPostData]:
        params = {
            "limit": 20,
            "offset": offset,
            "reblog_info": True,
        }
        response = self.api_request("GET", "user/dashboard", params=params)
        if not response:
            raise NotImplementedError("No posts found.")
        return [TumblrPostData(**post) for post in response["posts"]]

    def get_posts(self, blog_name: str, offset: int = 0) -> None:
        params = {
            "limit": 20,
            "offset": offset,
            "reblog_info": True,
        }

        response = self.api_request("GET", f"blog/{blog_name}.tumblr.com/posts", params=params)
        return [TumblrPostData(**post) for post in response["posts"]]

    def subscribe(self, blog_name: str) -> None:
        response = self.api_request("POST", "user/follow", json={"url": f"{blog_name}.tumblr.com"})
        assert response["blog"]["followed"] is True, response

    def unsubscribe(self, blog_name: str) -> None:
        response = self.api_request("POST", "user/unfollow", json={"url": f"{blog_name}.tumblr.com"})
        assert response["blog"]["followed"] is False, response

    def download_file(self, *args, **kwargs) -> FileSubclass:
        headers = kwargs.pop("headers", {})
        headers["accept"] = "image/*, video/*"
        return super().download_file(*args, headers=headers, **kwargs)


class TumblrPostData(BaseModel):
    id: int
    note_count: int
    timestamp: datetime

    type: str

    blog_name: str

    reblog: dict

    body: str | None = None
    reblogged_root_name: str | None = None
    photos: list[dict] | None = None
    video_type: str | None = None
    video_url: str | None = None

    @property
    def assets(self) -> list[str]:
        assets = []
        if self.type == "photo":
            assert self.photos
            for image_json in self.photos:
                all_sizes = image_json["alt_sizes"] + [image_json["original_size"]]
                highest = max(all_sizes, key=lambda x: x["height"] * x["width"])
                assets.append(highest["url"])

        elif self.type == "video":
            assert self.video_type, self._raw_data
            if self.video_type == "tumblr":
                assets.append(self.video_url)

        elif self.type == "answer":
            # https://beshinoe.tumblr.com/post/712945049861865472
            results = extract_urls_from_string(self.reblog["comment"], blacklist_images=False)
            assets += [result for result in results if re.match(r".*tumblr\.com.*\.\w+$", result)]

        elif self.type == "text":
            assert self.body
            parsed_body = BeautifulSoup(self.body, "html5lib")
            assets += [img["src"] for img in parsed_body.select("img")]

        elif self.type in ["link", "quote", "audio", "chat"]:
            return []

        else:
            raise NotImplementedError(self.type)

        return assets


class TumblrBlogData(BaseModel):
    title: str
    name: str
    description: str

    theme: dict
    avatar: list[dict]

    @property
    def related_urls(self) -> list[Url]:
        return [Url.parse(u) for u in extract_urls_from_string(self.description)]

    @property
    def header_url(self) -> str:
        return self.theme["header_image"]

    @property
    def avatar_url(self) -> str:
        return max(self.avatar, key=lambda x: x["width"])["url"]
