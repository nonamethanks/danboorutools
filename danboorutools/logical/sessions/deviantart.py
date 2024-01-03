from __future__ import annotations

import json
import os
from functools import cached_property

import deviantart
import ring

from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.twitter import TwitterArtistUrl
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class DeviantartSession(Session):
    @ring.lru()
    def user_data(self, username: str) -> DeviantartUserData:
        response = self.get(f"https://www.deviantart.com/{username}")
        parsed_json = response.search_json(
            pattern=r'window.__INITIAL_STATE__ = JSON.parse\("(.*)"\);',
            post_process=lambda x: x.encode("utf-8").decode("unicode_escape"),
        )

        about_data, = (module for module in parsed_json["modules"].values() if module["type"] == "about")

        return DeviantartUserData(**about_data["moduleData"])

    @cached_property
    def api(self) -> deviantart.Api:
        return deviantart.Api(
            os.environ["DEVIANTART_CLIENT_ID"],
            os.environ["DEVIANTART_CLIENT_SECRET"],
        )

    @ring.lru()
    def get_followed_artists(self) -> list[str]:
        artists = []
        offset = 0
        while True:
            get_data = {
                "offset": offset,
                "limit": 50,
                "mature_content": True,
            }
            page_json = self.api._req("/user/friends/" + os.environ["DEVIANTART_USERNAME"], get_data=get_data)

            artists += [artist_data["user"]["username"]
                        for artist_data in page_json["results"]
                        if artist_data["watch"]["deviations"]]

            if not page_json["has_more"]:
                return artists

            offset = page_json["next_offset"]

    @ring.lru()
    def get_artist_posts(self, artist: str, offset: int = 0) -> DeviantartPostsApiData:
        get_data = {
            "username": artist,
            "offset": offset,
            "limit": 24,
            "mature_content": True,
        }
        page_json = self.api._req("/gallery/all", get_data=get_data)
        return DeviantartPostsApiData(**page_json)

    @ring.lru()
    def get_download_url(self, uuid: str) -> str:
        data = self.api._req(f"/deviation/download/{uuid}", get_data={"mature_content": True})
        return data["src"]


class DeviantartUserData(BaseModel):
    username: str
    website: str
    twitterUsername: str | None
    textContent: dict
    socialLinks: list

    @property
    def related_urls(self) -> list[Url]:
        urls = [Url.parse(data["value"]) for data in self.socialLinks]

        if self.twitterUsername:
            urls += [TwitterArtistUrl.build(username=self.twitterUsername)]

        if self.website:
            website = self.website if self.website.startswith("http") else f"https://{self.website}"
            urls += [Url.parse(website)]

        if description := self.textContent["html"]:
            if description["type"] == "writer":
                urls += [Url.parse(u) for u in extract_urls_from_string(description["markup"])]
            elif description["type"] == "draft":
                data = json.loads(description["markup"])
                for entity in data["entityMap"].values():
                    if entity["type"] in ["DA_OFF_EMOTE", "wix-draft-plugin-image"]:
                        continue
                    if entity["type"] != "LINK":
                        raise NotImplementedError(entity)
                    entity_url = entity["data"]["url"]  # type: str
                    if not entity_url.startswith("http"):
                        entity_url = f"https://{entity_url}"
                    urls += [Url.parse(entity_url)]
            else:
                raise NotImplementedError(description)

        return list(dict.fromkeys(urls))


class DeviantartPostData(BaseModel):
    url: str
    deviationid: str
    published_time: int

    is_downloadable: bool
    stats: dict

    content: dict


class DeviantartPostsApiData(BaseModel):
    has_more: bool
    next_offset: int | None
    results: list[DeviantartPostData]
