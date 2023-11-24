from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel


class SoundcloudSession(Session):
    def artist_data(self, username: str) -> SoundcloudArtistData:
        json_data = self.extract_json_from_html(f"https://soundcloud.com/{username}", pattern=r"window.__sc_hydration = (.*);")
        artist_data = json_data[-1]["data"]
        return SoundcloudArtistData(**artist_data)


class SoundcloudArtistData(BaseModel):
    username: str
    description: str
