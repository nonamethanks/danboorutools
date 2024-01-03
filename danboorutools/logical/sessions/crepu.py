from __future__ import annotations

from typing import TYPE_CHECKING

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel

if TYPE_CHECKING:
    from danboorutools.models.url import Url


class CrepuSession(Session):
    def artist_data(self, username: str) -> CrepuArtistData:
        artist_data = self.get(f"https://api.crepu.net/api/v1.0/user_crepu_id?crepu_id={username}").json()
        return CrepuArtistData(**artist_data["data"])


class CrepuArtistData(BaseModel):
    user_name: str
    user_crepu_id: str

    user_circle_name: str | None
    user_twitter_url: str | None
    user_instagram_url:  str | None
    user_pixiv_url:  str | None
    user_genseki_url:  str | None
    user_taittsuu_url:  str | None
    user_url: str | None

    user_profile: str

    @property
    def related_urls(self) -> list[Url]:
        from danboorutools.models.url import Url
        return [
            Url.parse(url)
            for url in [
                self.user_twitter_url,
                self.user_instagram_url,
                self.user_pixiv_url,
                self.user_genseki_url,
                self.user_taittsuu_url,
                self.user_url,
            ]
            if url
        ]
