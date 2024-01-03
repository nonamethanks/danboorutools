from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel


class SoundcloudSession(Session):
    def artist_data(self, username: str) -> SoundcloudArtistData:
        json_data = self.get(f"https://soundcloud.com/{username}").search_json(pattern=r"window.__sc_hydration = (.*);")
        artist_data = json_data[-1]["data"]
        return SoundcloudArtistData(**artist_data)


class SoundcloudArtistData(BaseModel):
    username: str
    description: str | None
