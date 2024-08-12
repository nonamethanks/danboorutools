from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel


class LofterSession(Session):
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Android 14; Mobile; rv:115.0) Gecko/115.0 Firefox/115.0"

    def blog_data(self, blog_name: str) -> LofterBlogData:
        response = self.get(f"https://{blog_name}.lofter.com")
        raw_data = response.search_json(pattern=r"window.__initialize_data__ = (.*)")
        data = raw_data["blogData"]["data"]["blogInfo"]
        return LofterBlogData(**data)


class LofterBlogData(BaseModel):
    blogNickName: str
    blogName: str
    selfIntro: str
