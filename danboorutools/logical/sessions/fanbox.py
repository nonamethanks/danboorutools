from __future__ import annotations

import html
import json
import os
from datetime import datetime
from typing import TYPE_CHECKING

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url, parse_list
from danboorutools.util.misc import BaseModel

if TYPE_CHECKING:
    from danboorutools.logical.urls.fanbox import FanboxArtistImageUrl


class FanboxSession(Session):
    def artist_data(self, username: str) -> FanboxArtistData:
        headers = {"Origin": f"https://{username}.fanbox.cc", "Referer": f"https://{username}.fanbox.cc/"}
        artist_data = self.get_and_parse_fanbox_json(f"https://api.fanbox.cc/creator.get?creatorId={username}", headers=headers)
        return FanboxArtistData(**artist_data)

    def post_data(self, post_id: int) -> FanboxPostData:
        post_json = self.get_and_parse_fanbox_json(f"https://api.fanbox.cc/post.info?postId={post_id}")
        return FanboxPostData(**post_json)

    def get_and_parse_fanbox_json(self, json_url: str, *args, **kwargs) -> dict:
        kwargs["headers"] = {"Origin": "https://www.fanbox.cc"} | kwargs.get("headers", {})
        kwargs["cookies"] = {"FANBOXSESSID": os.environ["FANBOX_FANBOXSESSID"]} | kwargs.get("cookies", {})

        data = self.get(json_url, *args, **kwargs).json()
        if data.get("error") == "general_error":
            raise NotImplementedError(f"Couldn't get the data from {json_url}: {data}")

        return data["body"]

    def subscribe(self, username: str) -> None:
        cookies = {"FANBOXSESSID": os.environ["FANBOX_FANBOXSESSID"]}
        self.cookies.clear()
        html_request = self.get(f"https://{username}.fanbox.cc", cookies=cookies, skip_cache=True)
        metadata_content = html_request.html.select_one("#metadata").attrs["content"]
        metadata = json.loads(html.unescape(metadata_content))
        if not metadata["context"]["user"]["userId"]:
            raise NotImplementedError(f"Failed to login! Cookies: {cookies}")

        headers = {
            "Origin": f"https://{username}.fanbox.cc",
            "Referer": f"https://{username}.fanbox.cc/",
            "x-csrf-token": metadata["csrfToken"],
        }

        user_id = self.artist_data(username).user.userId

        response = self.post(
            "https://api.fanbox.cc/follow.create",
            headers=headers,
            cookies=cookies,
            json={"creatorUserId": user_id},
        )

        if not response.ok:
            try:
                if response.json()["body"]["type"] == "already_followed":
                    return
            except KeyError as e:
                e.add_note(f"Response: {response.json()}; metadata: {metadata}")
                raise
            raise NotImplementedError(response.json())
        if response.json()["body"] is None:
            return

        raise NotImplementedError(response.content)


class _UserData(BaseModel):
    name: str       # display name
    userId: int     # pixiv ID
    iconUrl: str


class FanboxArtistData(BaseModel):
    user: _UserData
    profileLinks: list[str]
    profileItems: list[dict]
    creatorId: str  # url username

    coverImageUrl: str

    @property
    def related_urls(self) -> list[Url]:
        from danboorutools.logical.urls.pixiv import PixivArtistUrl

        results = [Url.parse(link) for link in self.profileLinks]
        pixiv_url = PixivArtistUrl.build(user_id=self.user.userId)
        if pixiv_url not in results:
            # you never know with these sites
            results += [pixiv_url]

        return results

    @property
    def featured_images(self) -> list[FanboxArtistImageUrl]:
        images = []
        for url in self.profileItems:
            if url["type"] == "image":
                images.append(url["imageUrl"])
            else:
                raise NotImplementedError(url, self.profileItems, self)

        from danboorutools.logical.urls.fanbox import FanboxArtistImageUrl
        return parse_list(images, FanboxArtistImageUrl)


class FanboxPostData(BaseModel):
    id: int

    creatorId: str  # actually the name, not the id

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
