from __future__ import annotations

import copy
import os
import warnings
from datetime import datetime
from typing import TYPE_CHECKING

from requests.adapters import HTTPAdapter
from urllib3.exceptions import InsecureRequestWarning

from danboorutools.exceptions import NotAnUrlError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string

if TYPE_CHECKING:
    from requests import Response


class ArtstationSession(Session):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.mount("https://", HTTPAdapter(pool_connections=1))
        self.verify = False
        self.cert = None
        self.trust_env = False

    def request(self, *args, verify: bool = False, **kwargs) -> Response:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", InsecureRequestWarning)
            return super().request(*args, verify=verify, **kwargs)

    def artist_data(self, username: str) -> ArtstationArtistData:
        response = self.get_json(f"https://www.artstation.com/users/{username}.json")
        return ArtstationArtistData(**response)

    def get_followed_artists(self) -> list[str]:
        username = os.environ["ARTSTATION_USERNAME"]
        artists: set[str] = set()
        page = 1
        while True:
            response = self.get_json(f"https://www.artstation.com/users/{username}/following.json?page={page}")
            artists |= {user["subdomain"] for user in response["data"]}
            if len(artists) < response["total_count"]:
                page += 1
            else:
                return list(artists)

    def post_data(self, post_id: str) -> ArtstationPostData:
        url = f"https://www.artstation.com/projects/{post_id}.json"
        response = self.get_json(url)
        return ArtstationPostData(**response)

    def get_posts_from_artist(self, artist: str, page: int) -> list[ArtstationPostData]:
        url = f"https://www.artstation.com/users/{artist}/projects.json?page={page}"
        json_data = self.get_json(url)["data"]
        return [ArtstationPostData(**post_data) for post_data in json_data]


class ArtstationArtistData(BaseModel):
    id: int
    social_profiles: list[dict]

    full_name: str
    username: str

    @property
    def related_urls(self) -> list[Url]:
        parsed_urls: list[Url] = []
        for profile_data in self.social_profiles:
            if profile_data["social_network"] == "public_email":
                continue
            try:
                parsed_urls.append(Url.parse(profile_data["url"]))
            except NotAnUrlError:
                pass

        data = copy.deepcopy(self._raw_data)

        for value in ["profile_artstation_website_url", "artstation_url",
                      "large_avatar_url", "medium_avatar_url", "default_cover_url", "software_items",
                      "social_profiles"]:
            data.pop(value)

        parsed_urls += list(map(Url.parse, extract_urls_from_string(str(data))))

        return list(set(parsed_urls))


class ArtstationPostData(BaseModel):
    assets: list

    permalink: str

    created_at: datetime
    likes_count: int

    user: dict
