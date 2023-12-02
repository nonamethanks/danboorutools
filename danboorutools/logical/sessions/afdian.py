from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string


class AfdianSession(Session):
    def artist_data(self, username: str) -> AfdianArtistData:
        response = self.get_json(f"https://afdian.net/api/user/get-profile-by-slug?url_slug={username}")
        return AfdianArtistData(**response["data"]["user"])


class AfdianArtistData(BaseModel):
    name: str
    creator: dict

    @property
    def related_urls(self) -> list[Url]:
        return [Url.parse(url) for url in extract_urls_from_string(self.creator["detail"])]
