from __future__ import annotations

import os
from functools import cached_property

from pytumblr import TumblrRestClient

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string, memoize


class TumblrSession(Session):
    @cached_property
    def api(self) -> TumblrRestClient:
        return TumblrRestClient(
            os.environ["TUMBLR_CONSUMER_KEY"],
            os.environ["TUMBLR_CONSUMER_SECRET"],
            os.environ["TUMBLR_ACCESS_TOKEN"],
            os.environ["TUMBLR_ACCESS_TOKEN_SECRET"],
        )

    @memoize
    def blog_data(self, blog_name: str) -> TumblrBlogData:
        blog_data = self.api.blog_info(blog_name)
        return TumblrBlogData(**blog_data["blog"])


class TumblrBlogData(BaseModel):
    title: str
    name: str
    description: str

    @property
    def related_urls(self) -> list[Url]:
        return [Url.parse(u) for u in extract_urls_from_string(self.description) ]
