from __future__ import annotations

import os
import re
from datetime import datetime
from functools import cached_property

import ring
from bs4 import BeautifulSoup
from requests_oauthlib import OAuth1

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string


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

    @ring.lru()
    def blog_data(self, blog_name: str) -> TumblrBlogData:
        params = {"api_key": os.environ["TUMBLR_CONSUMER_KEY"]}
        response = self.get_json(f"https://api.tumblr.com/v2/blog/{blog_name}/info", params=params, auth=self.oauth)
        response = self._validate_api_response(response)
        return TumblrBlogData(**response["blog"])

    @ring.lru()
    def get_feed(self, limit: int | None = None, offset: int | None = None) -> list[TumblrPostData]:
        params = {
            "limit": limit or 20,
            "offset": offset or 0,
            "reblog_info": True,
        }
        response = self.get_json("https://api.tumblr.com/v2/user/dashboard", params=params, auth=self.oauth)
        response = self._validate_api_response(response)
        if not response:
            raise NotImplementedError("No posts found.")
        return [TumblrPostData(**post) for post in response["posts"]]


class TumblrPostData(BaseModel):
    id: int
    note_count: int
    timestamp: datetime

    type: str
    video_type: str | None
    video_url: str | None
    thumbnail_url: str | None

    photos: list[dict] | None

    blog_name: str
    reblogged_root_name: str | None

    reblog: dict
    body: str | None

    @property
    def assets(self) -> list[str]:
        assets = []
        if self.type == "photo":
            assert self.photos
            for image_json in self.photos:
                all_sizes = image_json["alt_sizes"] + [image_json["original_size"]]
                highest = sorted(all_sizes, key=lambda x: x["height"] * x["width"])[-1]
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

    @property
    def related_urls(self) -> list[Url]:
        return [Url.parse(u) for u in extract_urls_from_string(self.description)]
