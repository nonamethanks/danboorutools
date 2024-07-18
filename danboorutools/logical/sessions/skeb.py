from __future__ import annotations

import json
import os

from danboorutools import logger, settings
from danboorutools.exceptions import NotAuthenticatedError
from danboorutools.logical.sessions import ScraperResponse, Session
from danboorutools.logical.sessions.twitter import _twitter_login_through_form
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


class SkebSession(Session):
    def request(self, *args, is_retry: bool = False, **kwargs) -> ScraperResponse:
        if is_retry:
            self.login()
        kwargs["headers"] = kwargs.get("headers", {}) | {"Authorization": f"Bearer {self.bearer}"}
        try:
            request = super().request(*args, **kwargs)
        except NotAuthenticatedError:
            if is_retry:
                raise
            return self.request(*args, is_retry=True, **kwargs)
        else:
            return request

    def artist_data(self, username: str) -> SkebArtistData:
        response = self.get(
            f"https://skeb.jp/api/users/{username}",
            headers={
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
            },
        ).json()

        return SkebArtistData(**response)

    @property
    def bearer(self) -> str:
        bearer = (settings.BASE_FOLDER / "cookies" / "skeb_bearer.txt").read_text(encoding="utf-8")
        return bearer

    def login(self) -> None:
        logger.info("Logging into skeb.")
        browser = self.browser
        browser.get("https://skeb.jp")
        sign_in = browser.find_elements_by_text("Sign in")
        sign_in[-1].click()

        username = browser.find_element("name", "session[username_or_email]")
        password = browser.find_element("name", "session[password]")

        username.send_keys(os.environ["TWITTER_EMAIL"])
        password.send_keys(os.environ["TWITTER_PASSWORD"])

        browser.find_element("css selector", "label[for='remember']").click()

        browser.find_element("css selector", "[type='submit']").click()

        if browser.find_elements_by_text("Sign in to X"):
            self._twitter_login()

        assert browser.current_url == "https://skeb.jp/"

        for request in reversed(browser.requests):
            if "api/auth/x" in request.url:
                bearer = json.loads(request.response.body)["access_token"]
                logger.info("Updating saved skeb bearer.")
                (settings.BASE_FOLDER / "cookies" / "skeb_bearer.txt").write_text(bearer, encoding="utf-8")
                break
        else:
            raise NotImplementedError("Bearer token not found.")

    _twitter_login = _twitter_login_through_form

    # def login(self) -> None:
    #     self.cookies.clear()
    #     email = os.environ["TWITTER_EMAIL"]
    #     password = os.environ["TWITTER_PASSWORD"]

    #     response = super(self.__class__, self).request("POST", "https://skeb.jp/api/auth/twitter")
    #     oauth_url = response.url
    #     assert oauth_url.startswith("https://api.twitter.com/oauth/authenticate?oauth_token="), oauth_url
    #     assert (auth_token_el := response.html.select_one("input[name='authenticity_token']"))

    #     data = {
    #         "authenticity_token": auth_token_el.attrs["value"],
    #         "redirect_after_login": oauth_url,
    #         "force_login": False,
    #         "oauth_token": ParsableUrl(oauth_url).query["oauth_token"],
    #         "session[username_or_email]": email,
    #         "session[password]": password,
    #         "remember_me": "1",
    #     }
    #     headers = {
    #         "origin": "https://api.twitter.com",
    #         "referer": oauth_url,
    #     }
    #     response = super(self.__class__, self).request("POST", "https://api.twitter.com/oauth/authenticate", data=data, headers=headers)
    #     skeb_callback = response.html.select_one("a.maintain-context").attrs["href"]
    #     response = super(self.__class__, self).request("GET", skeb_callback, skip_cache=True)

    #     location = response.history[0].headers["Location"]
    #     bearer = ParsableUrl(location).query["auth_token"]
    #     (settings.BASE_FOLDER / "cookies" / "skeb_bearer.txt").write_text(bearer, encoding="utf-8")
    #     self.save_cookies("_interslice_session")

    def get_feed(self, offset: int | None = None, limit: int | None = None) -> list[SkebPostFromPageData]:
        username = os.environ["SKEB_USERNAME"]
        offset = offset or 0
        limit = limit or 90
        feed_data = self.get(f"https://skeb.jp/api/users/{username}/following_works?sort=date&offset={offset}&limit={limit}").json()
        if not feed_data:
            raise NotImplementedError("No posts found. Check cookies.")
        if not isinstance(feed_data, list):
            raise NotImplementedError(feed_data)
        return [SkebPostFromPageData(**post) for post in feed_data]

    def get_posts(self, username: str, offset: int) -> list[SkebPostData]:
        url = f"https://skeb.jp/api/users/{username}/works?role=creator&sort=date&offset={offset}"
        response = self.get(url).json()
        return [SkebPostFromPageData(**post) for post in response]

    def get_post_data(self, /, post_id: int, username: str) -> SkebPostData:
        headers = {"Referer": f"https://skeb.jp/@{username}/works/{post_id}"}
        post_data = self.get(f"https://skeb.jp/api/users/{username}/works/{post_id}", headers=headers).json()
        return SkebPostData(**post_data)

    def subscribe(self, username: str) -> None:
        headers = {"Referer": f"https://skeb.jp/@{username}"}
        resp = self.post(f"https://skeb.jp/api/users/{username}/follow", headers=headers).json()
        assert resp["following"] is True, resp

    def unsubscribe(self, username: str) -> None:
        headers = {"Referer": f"https://skeb.jp/@{username}"}
        resp = self.delete(f"https://skeb.jp/api/users/{username}/unfollow", headers=headers).json()
        assert resp["following"] is False, resp


class SkebPostFromPageData(BaseModel):
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
    enty_id: int | None = None
    fanbox_id: str | None
    fantia_id: int | None
    fanza_id: int | None
    # foriio: bool  # seems this is only true if `url` is set to xfolio.jp?
    nijie_id: int | None
    patreon_id: str | None
    pixiv_id: int | None
    skima_id: int | None
    twitter_uid: int
    # twitter_screen_name: str | None  # for some reason it can be None even if twitter_uid is not
    youtube_id: str | None

    user_service_links: list[dict[str, str]]

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

        # if self.twitter_screen_name:
        #     urls += [TwitterArtistUrl.build(username=self.twitter_screen_name)]

        if self.youtube_id:
            urls += [YoutubeChannelUrl.build(channel_id=self.youtube_id)]

        if self.url:
            urls.append(Url.parse(self.url))

        for data in self.user_service_links:
            if data["provider"] == "twitter":
                urls += [TwitterArtistUrl.build(username=data["screen_name"])]
            else:
                raise NotImplementedError(data)

        urls += [Url.parse(u) for u in extract_urls_from_string(self.description)]

        return list(dict.fromkeys(urls))
