from __future__ import annotations

import os

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, memoize


class ArtstationSession(Session):
    @memoize
    def artist_data(self, username: str) -> ArtstationArtistData:
        response = self.get_json_cached(f"https://www.artstation.com/users/{username}.json")
        return ArtstationArtistData(**response)

    @memoize
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

    @memoize
    def post_data(self, post_id: str) -> ArtstationPostData:
        url = f"https://www.artstation.com/projects/{post_id}.json"
        response = self.get_json(url)
        return ArtstationPostData(**response)


class ArtstationArtistData(BaseModel):
    id: int
    social_profiles: list[dict]

    full_name: str
    username: str

    @property
    def related_urls(self) -> list[Url]:
        urls = [
            Url.parse(u["url"])
            for u in self.social_profiles
            if u["social_network"] != "public_email"
        ]

        internal_urls = ["profile_artstation_website_url", "artstation_url",
                         "large_avatar_url", "medium_avatar_url", "default_cover_url", "software_items"]
        for url_value in {v for k, v in self._raw_data.items() if k.endswith("_url") and v and k not in internal_urls}:
            urls += [Url.parse(url_value)]

        return list(dict.fromkeys(urls))


class ArtstationPostData(BaseModel):
    likes_count: int
    assets: list
