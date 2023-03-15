from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, memoize


class ArtstationSession(Session):
    @memoize
    def artist_data(self, username: str) -> ArtstationArtistData:
        response = self.get_json_cached(f"https://www.artstation.com/users/{username}.json")
        return ArtstationArtistData(**response)


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
