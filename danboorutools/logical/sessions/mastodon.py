from __future__ import annotations

import os

from mastodon import Mastodon

from danboorutools.logical.extractors.pixiv import PixivArtistUrl
from danboorutools.logical.sessions import Session
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
            raise NotImplementedError(domain)
        return Mastodon(
            client_id=os.environ[f"{site}_CLIENT_ID"],
            client_secret=os.environ[f"{site}_CLIENT_SECRET"],
            access_token=os.environ[f"{site}_ACCESS_TOKEN"],
            api_base_url=f"https://{domain}",
            version_check_mode="none"
        )

    @memoize
    def user_data(self, domain: str, /, user_id: int | None = None, username: str | None = None) -> MastodonArtistData:
        api = self.api(domain)
        if username:
            for user in api.account_search(f"{username}@{domain}"):
                if user["username"] == username:
                    return MastodonArtistData(**user)
            else:
                raise NotImplementedError(username)
        elif user_id:
            user_data = api.account(user_id)
        else:
            raise NotImplementedError
        return MastodonArtistData(**user_data)


class MastodonArtistData(BaseModel):
    id: int
    username: str
    display_name: str

    note: str
    fields: list[dict]
    oauth_authentications: list[dict]

    @property
    def related_urls(self) -> list[Url]:
        urls = [Url.parse(u) for u in extract_urls_from_string(self.note)]

        for auth_data in self.oauth_authentications:
            if auth_data["provider"] == "pixiv":
                urls += [Url.build(PixivArtistUrl, user_id=int(auth_data["uid"]))]
            else:
                raise NotImplementedError(auth_data, self.username)

        for field in self.fields:
            urls += [Url.parse(u) for u in extract_urls_from_string(field["value"])]

        return list(dict.fromkeys(urls))
