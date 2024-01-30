from __future__ import annotations

import copy
import os
import warnings
from datetime import datetime

from backoff import constant, on_exception
from requests.adapters import HTTPAdapter
from urllib3.exceptions import InsecureRequestWarning

from danboorutools.exceptions import HTTPError, MaintenanceError, NotAnUrlError, UnknownUrlError
from danboorutools.logical.sessions import ScraperResponse, Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class ArtstationSession(Session):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.mount("https://", HTTPAdapter(pool_connections=1))
        self.verify = False
        self.cert = None
        self.trust_env = False

    @on_exception(constant, MaintenanceError, max_tries=3, interval=5, jitter=None)
    def request(self, *args, verify: bool = False, **kwargs) -> ScraperResponse:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", InsecureRequestWarning)
            try:
                return super().request(*args, verify=verify, **kwargs)
            except HTTPError as e:
                if e.status_code == 502 and\
                        "ArtStation is currently undergoing maintenance and will be back online shortly!" in e.response.text:
                    raise MaintenanceError(e.response) from e
                raise

    def artist_data(self, username: str) -> ArtstationArtistData:
        response = self.get(f"https://www.artstation.com/users/{username}.json").json()
        return ArtstationArtistData(**response)

    def post_data(self, post_id: str) -> ArtstationPostData:
        url = f"https://www.artstation.com/projects/{post_id}.json"
        response = self.get(url).json()
        return ArtstationPostData(**response)

    def get_posts_from_artist(self, artist: str, page: int) -> list[ArtStationFeedPostData]:
        url = f"https://www.artstation.com/users/{artist}/projects.json?page={page}"
        json_data = self.get(url).json()["data"]
        return [ArtStationFeedPostData(**post_data) for post_data in json_data]

    def get_post_urls_from_feed(self, page: int) -> list[str]:
        cookies = {"ArtStationSessionCookie": os.environ["ARTSTATION_SESSION_COOKIE"]}
        url = f"https://www.artstation.com/api/v2/community/explore/projects/following.json?page={page}&dimension=all&per_page=30"
        json_data = self.get(url, cookies=cookies).json()["data"]
        if json_data is None:
            raise NotImplementedError("Cookie seems to have expired.")
        return [post["url"] for post in json_data]


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
            if profile_data["url"] == "http://":  # why...
                continue
            try:
                parsed_urls.append(Url.parse(profile_data["url"]))
            except NotAnUrlError:
                pass

        data = copy.deepcopy(self._raw_data)

        for value in ["profile_artstation_website_url", "artstation_url",
                      "large_avatar_url", "medium_avatar_url", "default_cover_url", "software_items",
                      "social_profiles", "badges"]:
            data.pop(value)

        portfolio = data.pop("portfolio")
        parsed_urls += list(map(Url.parse, extract_urls_from_string(portfolio["summary"])))
        if portfolio["resume_url"]:
            parsed_urls += [Url.parse(portfolio["resume_url"])]

        try:
            parsed_urls += list(map(Url.parse, extract_urls_from_string(str(data))))
        except UnknownUrlError as e:
            e.add_note(f"Data: {data}")
            raise

        return list(set(parsed_urls))


class ArtstationPostData(BaseModel):
    assets: list

    permalink: str

    created_at: datetime
    likes_count: int

    user: dict


class ArtStationFeedPostData(BaseModel):
    permalink: str
    hash_id: str

    created_at: datetime
    likes_count: int

    assets_count: int

    cover: dict
