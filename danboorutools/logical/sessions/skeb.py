from __future__ import annotations

import os
from typing import TYPE_CHECKING

import ring

from danboorutools import settings
from danboorutools.exceptions import HTTPError
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.booth import BoothArtistUrl
from danboorutools.logical.urls.fanbox import FanboxArtistUrl
from danboorutools.logical.urls.fantia import FantiaFanclubUrl
from danboorutools.logical.urls.fanza import FanzaDoujinAuthorUrl
from danboorutools.logical.urls.patreon import PatreonArtistUrl
from danboorutools.logical.urls.pixiv import PixivArtistUrl
from danboorutools.logical.urls.twitter import TwitterArtistUrl, TwitterIntentUrl
from danboorutools.logical.urls.youtube import YoutubeChannelUrl
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string

if TYPE_CHECKING:
    from requests import Response


class SkebSession(Session):
    def request(self, *args, is_retry: bool = False, **kwargs) -> Response:
        bearer = self.try_login_and_return_bearer()
        kwargs["headers"] = kwargs.get("headers", {}) | {"Authorization": f"Bearer {bearer}"}
        try:
            request = super().request(*args, **kwargs)
        except HTTPError as e:
            if e.status_code == 503:
                if is_retry:
                    raise
                self.try_login_and_return_bearer.storage.backend.clear()
                self.request(*args, is_retry=True, **kwargs)
            raise
        return request

    def artist_data(self, username: str) -> SkebArtistData:
        response = self.get(f"https://skeb.jp/api/users/{username}").json()

        return SkebArtistData(**response)

    @ring.lru()
    def try_login_and_return_bearer(self) -> str:
        try:
            self.load_cookies()
        except FileNotFoundError:
            self.login()
        bearer = (settings.BASE_FOLDER / "cookies" / "skeb_bearer.txt").read_text(encoding="utf-8")
        return bearer

    def login(self) -> None:
        email = os.environ["TWITTER_EMAIL"]
        password = os.environ["TWITTER_PASSWORD"]

        response = super().request("POST", "https://skeb.jp/api/auth/twitter")
        oauth_url = response.url
        assert oauth_url.startswith("https://api.twitter.com/oauth/authenticate?oauth_token="), oauth_url

        data = {
            "authenticity_token": response.html.select_one("input[name='authenticity_token']")["value"],
            "redirect_after_login": oauth_url,
            "force_login": False,
            "oauth_token": ParsableUrl(oauth_url).query["oauth_token"],
            "session[username_or_email]": email,
            "session[password]": password,
            "remember_me": "1",
        }
        headers = {
            "origin": "https://api.twitter.com",
            "referer": oauth_url,
        }
        response = super().request("POST", "https://api.twitter.com/oauth/authenticate", data=data, headers=headers)
        skeb_callback = response.html.select_one("a.maintain-context")["href"]
        response = super().request("GET", skeb_callback, skip_cache=True)

        bearer = ParsableUrl(response.history[0].headers["Location"]).query["auth_token"]
        (settings.BASE_FOLDER / "cookies" / "skeb_bearer.txt").write_text(bearer, encoding="utf-8")
        self.save_cookies("_interslice_session")

    def get_feed(self, offset: int | None = None, limit: int | None = None) -> list[SkebPostFeedData]:
        username = os.environ["SKEB_USERNAME"]
        offset = offset or 0
        limit = limit or 90
        feed_data = self.get(f"https://skeb.jp/api/users/{username}/following_works?sort=date&offset={offset}&limit={limit}").json()
        if not feed_data:
            raise NotImplementedError("No posts found. Check cookies.")
        if not isinstance(feed_data, list):
            raise NotImplementedError(feed_data)
        return [SkebPostFeedData(**post) for post in feed_data]

    def get_post_data(self, /, post_id: int, username: str) -> SkebPostData:
        headers = {"Referer": f"https://skeb.jp/@{username}/works/{post_id}"}
        post_data = self.get(f"https://skeb.jp/api/users/{username}/works/{post_id}", headers=headers).json()
        return SkebPostData(**post_data)


class SkebPostFeedData(BaseModel):
    private: bool
    path: str


class SkebPostData(BaseModel):
    previews: list[dict]
    article_image_url: str | None


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
    patreon_id: str | None
    pixiv_id: int | None
    skima_id: int | None
    twitter_uid: int
    twitter_screen_name: str | None  # for some reason it can be None even if twitter_uid is not
    youtube_id: str | None

    @ property
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

        if self.fanbox_id and self.fanbox_id != "www":  # https://skeb.jp/@lenkenji21 lmao
            urls += [FanboxArtistUrl.build(username=self.fanbox_id)]

        if self.fantia_id:
            urls += [FantiaFanclubUrl.build(fanclub_id=self.fantia_id)]

        if self.fanza_id:
            urls += [FanzaDoujinAuthorUrl.build(user_id=self.fanza_id, subsubsite="dc")]

        if self.patreon_id:
            urls += [PatreonArtistUrl.build(username=self.patreon_id)]

        if self.pixiv_id:
            urls += [PixivArtistUrl.build(user_id=self.pixiv_id)]

        if self.skima_id:
            # urls += [SkimaArtistUrl.build(user_id=self.skima_id)]
            pass  # impossible to tell if it's a gallery id or an artist id

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
