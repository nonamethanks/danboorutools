from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel


class FanboxSession(Session):
    def artist_data(self, username: str) -> FanboxArtistData:
        headers = {"Origin": f"https://{username}.fanbox.cc", "Referer": f"https://{username}.fanbox.cc/"}
        response = self.get_json_cached(f"https://api.fanbox.cc/creator.get?creatorId={username}", headers=headers)
        return FanboxArtistData(**response["body"])


class _UserData(BaseModel):
    name: str       # display name
    userId: int     # pixiv ID


class FanboxArtistData(BaseModel):
    user: _UserData
    profileLinks: list[str]
    creatorId: str  # url username

    class Config:
        allow_population_by_field_name = True

    @property
    def related_urls(self) -> list[Url]:
        from danboorutools.logical.urls.pixiv import PixivArtistUrl

        results = [Url.parse(link) for link in self.profileLinks]
        pixiv_url = PixivArtistUrl.build(PixivArtistUrl, user_id=self.user.userId)
        if pixiv_url not in results:
            # you never know with these sites
            results += [pixiv_url]

        return results
