from __future__ import annotations

import os
from datetime import datetime

from mastodon import Mastodon
from mastodon.errors import MastodonNetworkError
from requests.exceptions import ReadTimeout

from danboorutools.logical.sessions import Session
from danboorutools.logical.urls.pixiv import PixivArtistUrl
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string, memoize


class MastodonSession(Session):
    @memoize
    def api(self, domain: str) -> Mastodon:
        if "pawoo.net" in domain:
            site = "PAWOO"
        elif "baraag.net" in domain:
            site = "BARAAG"
        else:
            site = "PAWOO"
            domain = "pawoo.net"  # backend developers hate this simple trick!
        return Mastodon(
            client_id=os.environ[f"{site}_CLIENT_ID"],
            client_secret=os.environ[f"{site}_CLIENT_SECRET"],
            access_token=os.environ[f"{site}_ACCESS_TOKEN"],
            api_base_url=f"https://{domain}",
            version_check_mode="none",
            session=self,
            request_timeout=self.DEFAULT_TIMEOUT,
        )

    @memoize
    def user_data(self, domain: str, /, user_id: int | None = None, username: str | None = None) -> MastodonArtistData:
        if not username and not user_id:
            raise ValueError(username, user_id)

        try:
            if username:
                user_data = self._user_data_from_username(domain=domain, username=username)
            elif user_id:
                user_data = self.api(domain).account(user_id)
        except MastodonNetworkError as e:
            if "Read timed out." in str(e):
                raise ReadTimeout from e
            raise
        else:
            return MastodonArtistData(**user_data)

    @memoize
    def _user_data_from_username(self, /, domain: str, username: str) -> dict:
        for user in self.api(domain).account_search(f"{username}@{domain}"):
            if user["username"] == username:
                return user
        raise NotImplementedError(domain, username)

    @memoize
    def get_feed(self, domain: str, max_id: int) -> list[MastodonPostData]:
        posts: list[dict] = self.api(domain).timeline_home(
            max_id=max_id or None,
            only_media=True,
            local=True,
            remote=False,
        )

        return [MastodonPostData(**post) for post in posts]


class MastodonArtistData(BaseModel):
    id: int
    username: str
    display_name: str

    note: str
    fields: list[dict]
    oauth_authentications: list[dict] | None

    @property
    def related_urls(self) -> list[Url]:
        urls = [Url.parse(u) for u in extract_urls_from_string(self.note)]

        if self.oauth_authentications:
            for auth_data in self.oauth_authentications:
                if auth_data["provider"] == "pixiv":
                    urls += [Url.build(PixivArtistUrl, user_id=int(auth_data["uid"]))]
                else:
                    raise NotImplementedError(auth_data, self.username)

        for field in self.fields:
            urls += [Url.parse(u) for u in extract_urls_from_string(field["value"])]

        return list(dict.fromkeys(urls))


class MastodonPostData(BaseModel):
    id: int
    url: str
    media_attachments: list[dict]
    created_at: datetime
    favourites_count: int

    @property
    def assets(self) -> list[str]:
        return [image_data["url"] for image_data in self.media_attachments]
