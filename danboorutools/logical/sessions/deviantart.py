from __future__ import annotations

import json
import os
import re
from datetime import datetime
from functools import cached_property

from backoff import constant, on_exception
from pydantic import Field
from pyrate_limiter.limiter import Limiter
from pyrate_limiter.request_rate import RequestRate

from danboorutools.exceptions import HTTPError
from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.twitter import TwitterArtistUrl
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string
from danboorutools.util.time import datetime_from_string


class DeviantartSession(Session):
    deviantart_api_limiter = limiter = Limiter(RequestRate(1, 4))
    MAX_CALLS_PER_SECOND = 0.3

    @cached_property
    def access_token(self) -> str:
        client_id = os.environ["DEVIANTART_CLIENT_ID"]
        client_secret = os.environ["DEVIANTART_CLIENT_SECRET"]

        resp = self.post(
            "https://www.deviantart.com/oauth2/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
        )
        return resp.json()["access_token"]

    def api_request(self, path: str, *args, **kwargs) -> dict:
        data = kwargs.pop("data", {}) | {"access_token": self.access_token}

        with self.deviantart_api_limiter.ratelimit(delay=True):
            response = self.post(
                f"https://www.deviantart.com/api/v1/oauth2/{path.strip("/")}",
                *args,
                data=data,
                **kwargs,
            )
        return response.json()

    def user_data(self, username: str, skip_cache: bool = False) -> DeviantartUserData:
        response = self.get(f"https://www.deviantart.com/{username}", skip_cache=skip_cache)
        parsed_json = response.search_json(
            pattern=r'window.__INITIAL_STATE__ = JSON.parse\("(.*)"\);',
            post_process=lambda x: x.encode("utf-8").decode("unicode_escape"),
        )

        modules = next(iter(parsed_json["@@gruser"]["grusers"].values()))["modules"]
        about_data, = (module for module in modules.values() if module["name"] == "about")

        return DeviantartUserData(**about_data["moduleData"]["about"] | {"session_data": parsed_json["@@publicSession"]})

    def get_posts(self, username: str, offset: int = 0) -> DeviantartPostsApiData:
        params = {
            "username": username,
            "offset": offset,
            "limit": 24,
            "mature_content": "true",
        }
        page_json = self.api_request("/gallery/all", params=params)
        return DeviantartPostsApiData(**page_json)

    @on_exception(constant, HTTPError, max_tries=2, interval=60 * 5, jitter=None)
    def get_post_data(self, deviation_id: int) -> DeviantartHTMLPostData:
        page = self.get(f"https://www.deviantart.com/deviation/{deviation_id}")
        data = page.search_json(
            pattern=r'window.__INITIAL_STATE__ = JSON.parse\("(.*)"\);',
            post_process=lambda x: x.encode("utf-8").decode("unicode_escape"),
        )
        return DeviantartHTMLPostData(**data)

    def get_download_url(self, uuid: str) -> str:
        data = self.api_request(f"/deviation/download/{uuid}", params={"mature_content": "true"})
        return data["src"]


class DeviantartUserData(BaseModel):
    username: str
    website: str
    twitterUsername: str | None
    textContent: dict
    socialLinks: list

    session_data: dict

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


class DeviantartPostsApiData(BaseModel):
    has_more: bool
    next_offset: int | None
    results: list[DeviantartPostData]


class DeviantartPostData(BaseModel):
    url: str
    deviationid: str
    published_time: datetime

    is_downloadable: bool
    stats: dict[str, int]

    content: dict


class DeviantartHTMLPostData(BaseModel):
    entities: dict[str, dict[str, dict]] = Field(alias="@@entities")

    @property
    def deviation(self) -> dict:
        return next(iter(self.entities["deviation"].values()))  # pylint: disable=unsubscriptable-object

    @property
    def deviation_extended(self) -> dict:
        return next(iter(self.entities["deviationExtended"].values()))  # pylint: disable=unsubscriptable-object

    @property
    def user(self) -> dict:
        return next(iter(self.entities["user"].values()))  # pylint: disable=unsubscriptable-object

    @property
    def download_token(self) -> str | None:
        try:
            return self.deviation["media"]["token"][1]
        except IndexError:
            return None

    @property
    def sample_token(self) -> str | None:
        try:
            return self.deviation["media"]["token"][0]
        except IndexError:
            return None

    @property
    def download_url(self) -> str | None:
        try:
            return self.deviation_extended["download"]["url"]
        except KeyError:
            return None

    @property
    def pretty_name(self) -> str:
        return self.deviation["media"]["prettyName"]

    @property
    def base_url(self) -> str:
        return self.deviation["media"]["baseUri"]

    @property
    def videos(self) -> list[dict]:
        try:
            types: list[dict] = self.deviation["media"]["types"]
        except KeyError:
            return []
        return [t for t in types if t["t"] == "video"]

    @property
    def v1_path(self) -> str:
        path = self.deviation["media"]["types"][0]["c"]
        return re.sub(r"<prettyName>[^.]*", self.pretty_name, path)

    @property
    def full_size(self) -> str:
        if self.download_token:
            file_ext = self.base_url.split(".")[-1]
            return f"{self.base_url}?token={self.download_token}&filename={self.pretty_name}.{file_ext}"
        elif self.download_url:
            # https://github.com/danbooru/danbooru/blob/master/app/logical/source/extractor/deviant_art.rb#L66
            raise ShouldDownloadError

        elif self.deviation["isDownloadable"]:
            raise ShouldDownloadError
        elif self.videos:
            return max(self.videos, key=lambda x: x["f"])["b"]
        elif self.sample_token:
            return f"{self.base_url}{self.v1_path}?token={self.sample_token}"

        raise NotImplementedError(self)

    @property
    def published_time(self) -> datetime:
        return datetime_from_string(self.deviation["publishedTime"])

    @property
    def favorites(self) -> int:
        return self.deviation["stats"]["favourites"]


class ShouldDownloadError(Exception):
    ...
