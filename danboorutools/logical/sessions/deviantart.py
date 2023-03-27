from __future__ import annotations

import json
import os
import re
from functools import cached_property

import deviantart

from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.twitter import TwitterArtistUrl
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, memoize

data_pattern = re.compile(r"window.__INITIAL_STATE__ = JSON.parse\(\"(.*)\"\);")


class DeviantartSession(Session):
    @memoize
    def user_data(self, username: str) -> DeviantartUserData:
        html = self.get_html(f"https://www.deviantart.com/{username}")
        script = next(el.string for el in html.select("script") if el.string and "window.__INITIAL_STATE__ = JSON.parse" in el.string)
        match = data_pattern.search(script)
        if not match:
            raise NotImplementedError(username)

        parsable_json = match.groups()[0].encode("utf-8").decode("unicode_escape")
        parsed_json = json.loads(parsable_json)

        about_data, = (module for module in parsed_json["modules"].values() if module["type"] == "about")

        return DeviantartUserData(**about_data["moduleData"])

    @cached_property
    def api(self) -> deviantart.Api:
        return deviantart.Api(
            os.environ["DEVIANTART_CLIENT_ID"],
            os.environ["DEVIANTART_CLIENT_SECRET"],
        )

    @memoize
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

    @memoize
    def get_artist_posts(self, artist: str, offset: int = 0) -> DeviantartPostsApiData:
        get_data = {
            "username": artist,
            "offset": offset,
            "limit": 24,
            "mature_content": True,
        }
        page_json = self.api._req("/gallery/all", get_data=get_data)
        return DeviantartPostsApiData(**page_json)

    @memoize
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
            urls += [Url.build(TwitterArtistUrl, username=self.twitterUsername)]

        if self.website:
            website = self.website if self.website.startswith("http") else f"https://{self.website}"
            urls += [Url.parse(website)]

        if self.textContent["html"]["markup"]:
            data = json.loads(self.textContent["html"]["markup"])
            for entity in data["entityMap"].values():
                if entity["type"] != "LINK":
                    raise NotImplementedError(entity)
                urls += [Url.parse(entity["data"]["url"])]

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
