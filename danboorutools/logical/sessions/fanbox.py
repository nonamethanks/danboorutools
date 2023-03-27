from __future__ import annotations

import os
from datetime import datetime

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, memoize


class FanboxSession(Session):
    def artist_data(self, username: str) -> FanboxArtistData:
        headers = {"Origin": f"https://{username}.fanbox.cc", "Referer": f"https://{username}.fanbox.cc/"}
        artist_data = self.get_and_parse_fanbox_json(f"https://api.fanbox.cc/creator.get?creatorId={username}", headers=headers)
        return FanboxArtistData(**artist_data)

    @memoize
    def post_data(self, post_id: int) -> FanboxPostData:
        post_json = self.get_and_parse_fanbox_json(f"https://api.fanbox.cc/post.info?postId={post_id}")
        return FanboxPostData(**post_json)

    def get_and_parse_fanbox_json(self, json_url: str, *args, use_cookies: bool = False, **kwargs) -> dict:
        kwargs["headers"] = {"Origin": "https://www.fanbox.cc"} | kwargs.get("headers", {})

        if use_cookies:
            kwargs["cookies"] = {"FANBOXSESSID": os.environ["FANBOX_FANBOXSESSID"]} | kwargs.get("cookies", {})

        data = self.get_json_cached(json_url, *args, **kwargs)
        if data.get("error") == "general_error":
            raise NotImplementedError(f"Couldn't get the data from {json_url}: {data}")

        return data["body"]


class _UserData(BaseModel):
    name: str       # display name
    userId: int     # pixiv ID


class FanboxArtistData(BaseModel):
    user: _UserData
    profileLinks: list[str]
    creatorId: str  # url username

    class Config:
        allow_population_by_field_name = True

    @property
    def related_urls(self) -> list[Url]:
        from danboorutools.logical.urls.pixiv import PixivArtistUrl

        results = [Url.parse(link) for link in self.profileLinks]
        pixiv_url = PixivArtistUrl.build(PixivArtistUrl, user_id=self.user.userId)
        if pixiv_url not in results:
            # you never know with these sites
            results += [pixiv_url]

        return results


class FanboxPostData(BaseModel):
    id: int

    creatorId: str

    likeCount: int
    publishedDatetime: datetime

    feeRequired: int

    body: dict | None

    @property
    def assets(self) -> list[str]:
        assets: list[str] = []
        if self.feeRequired:
            return assets

        assert self.body is not None
        assets += [i["originalUrl"] for i in self.body.get("images", [])]
        assets += [v["originalUrl"] for v in self.body.get("imageMap", {}).values()]
        assets += [v["url"] for v in self.body.get("fileMap", {}).values()]

        if "blocks" in self.body:
            image_positions = [i["imageId"] for i in self.body["blocks"] if i["type"] == "image"]
            image_index = {k: v for v, k in enumerate(image_positions)}
            assets.sort(key=lambda x: image_index.get(x.split("/")[-1].split(".")[0], 0))

        return assets
