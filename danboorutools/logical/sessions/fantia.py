from __future__ import annotations

import json
import os
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import validator

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from requests import Response


class FantiaSession(Session):
    @property
    def _cookies(self) -> dict:
        return {"_session_id": os.environ["FANTIA_SESSION_ID_COOKIE"]}

    def request(self, *args, **kwargs) -> Response:
        kwargs["cookies"] = self._cookies | kwargs.get("cookies", {})
        return super().request(*args, **kwargs)

    def get_feed(self, page: int) -> dict:
        page_json = self.get_json(f"https://fantia.jp/api/v1/me/timelines/posts?page={page}&per=24")
        return page_json

    def get_post_data(self, post_id: int) -> FantiaPostData:
        post_url = f"https://fantia.jp/posts/{post_id}"
        html = self.get_html(post_url)
        csrf = html.select_one("meta[name='csrf-token']")["content"]

        api_response = self.get_json(f"https://fantia.jp/api/v1/posts/{post_id}", headers={"X-CSRF-Token": csrf})
        if not api_response.get("post"):
            raise NotImplementedError(f"Could not parse fantia api response for {post_url}: {api_response}")

        return FantiaPostData(**api_response["post"])


class FantiaPostData(BaseModel):
    id: int
    posted_at: datetime
    likes_count: int

    thumb: dict
    post_contents: list[dict]

    @validator("posted_at", pre=True)
    def parse_created_at(cls, value: str) -> datetime:  # pylint: disable=no-self-argument # noqa: N805 # pydantic is retarded
        return datetime_from_string(value)

    @property
    def assets(self) -> list[str]:
        assets = []

        if self.thumb:
            assets.append(self.thumb["original"])

        for content in self.post_contents:
            if content["visible_status"] != "visible":
                continue

            if content["category"] == "photo_gallery":
                assets += [photo["url"]["original"] for photo in content["post_content_photos"]]
            elif content["category"] == "file":
                assets.append("https://fantia.jp/" + content["download_uri"].strip("/"))
            elif content["category"] == "blog":
                _json = json.loads(content["comment"])
                for subjson in _json["ops"]:
                    if isinstance(subjson["insert"], dict):
                        assets.append(subjson["insert"]["fantiaImage"]["url"])
            elif content["category"] in ["embed", "text"] and not content["content_type"]:
                pass
            else:
                raise NotImplementedError(content["category"], self.id)
        return assets
