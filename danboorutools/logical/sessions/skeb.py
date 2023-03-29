from __future__ import annotations

import os
from typing import TYPE_CHECKING

from danboorutools.exceptions import HTTPError, InvalidSkebCredentialsError
from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.booth import BoothArtistUrl
from danboorutools.logical.urls.fanbox import FanboxArtistUrl
from danboorutools.logical.urls.pixiv import PixivArtistUrl
from danboorutools.logical.urls.twitter import TwitterArtistUrl, TwitterIntentUrl
from danboorutools.logical.urls.youtube import YoutubeChannelUrl
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string

if TYPE_CHECKING:
    from requests import Response


class SkebSession(Session):
    _bearer_cookie = os.environ["SKEB_BEARER_TOKEN"]

    @property
    def cookies_from_env(self) -> dict:
        return {
            "_interslice_session": os.environ["SKEB_COOKIE_INTERSLICE_SESSION"],
        }.copy()

    def request(self, *args, **kwargs) -> Response:
        kwargs["cookies"] = self.cookies_from_env
        kwargs["headers"] = kwargs.get("headers", {}) | {"Authorization": f"Bearer {self._bearer_cookie}"}
        try:
            request = super().request(*args, **kwargs)
        except HTTPError as e:
            if e.status_code == 503:
                raise InvalidSkebCredentialsError from e
            raise
        return request

    def artist_data(self, username: str) -> SkebArtistData:
        response = self.get_json(f"https://skeb.jp/api/users/{username}")

        return SkebArtistData(**response)


class SkebArtistData(BaseModel):
    name: str
    screen_name: str
    description: str
    url: str | None

    booth_id: str | None
    coconala_id: int | None
    dlsite_id: int | None
    enty_id: int | None
    fanbox_id: str | None
    fantia_id: int | None
    fanza_id: int | None
    # foriio: bool  # seems this is only true if `url` is set to xfolio.jp?
    nijie_id: int | None
    patreon_id: int | None
    pixiv_id: int | None
    skima_id: int | None
    twitter_uid: int
    twitter_screen_name: str | None  # for some reason it can be None even if twitter_uid is not
    youtube_id: str | None

    @property
    def related_urls(self) -> list[Url]:  # pylint: disable=too-many-branches
        urls: list[Url] = []

        if self.booth_id:
            urls += [BoothArtistUrl.build(username=self.booth_id)]

        if self.coconala_id:
            raise NotImplementedError(self.coconala_id)

        if self.dlsite_id:
            raise NotImplementedError(self.dlsite_id)

        if self.enty_id:
            raise NotImplementedError(self.enty_id)

        if self.fanbox_id:
            urls += [FanboxArtistUrl.build(username=self.fanbox_id)]

        if self.fantia_id:
            raise NotImplementedError(self.fantia_id)

        if self.fanza_id:
            raise NotImplementedError(self.fanza_id)

        if self.patreon_id:
            raise NotImplementedError(self.patreon_id)

        if self.pixiv_id:
            urls += [PixivArtistUrl.build(user_id=self.pixiv_id)]

        if self.skima_id:
            raise NotImplementedError(self.skima_id)

        if self.twitter_uid:
            urls += [TwitterIntentUrl.build(intent_id=self.twitter_uid)]

        if self.twitter_screen_name:
            urls += [TwitterArtistUrl.build(username=self.twitter_screen_name)]

        if self.youtube_id:
            urls += [YoutubeChannelUrl.build(channel_id=self.youtube_id)]

        if self.url:
            urls.append(Url.parse(self.url))

        urls += [Url.parse(u) for u in extract_urls_from_string(self.description)]

        return list(dict.fromkeys(urls))
