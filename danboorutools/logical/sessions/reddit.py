from __future__ import annotations

import re

import ring

from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url

BEARER_TOKEN_PATTERN = re.compile(r"accessToken\":\"([\w-]+)\"")


class RedditSession(Session):
    bearer_token: str | None = None

    @ring.lru()
    def get_social_links(self, username: str) -> list[Url]:
        if not self.bearer_token:
            response = self.get(f"https://www.reddit.com/user/{username}", cached=True)
            match = BEARER_TOKEN_PATTERN.search(response.text)
            if not match:
                raise NotImplementedError(username, response.status_code)
            self.bearer_token = match.groups()[0]

        response = self.post(
            "https://gql.reddit.com/",
            json={"id": "11a239b07f86", "variables": {"username": username}},
            headers={"Authorization": f"Bearer {self.bearer_token}"},
        )
        return [Url.parse(url["outboundUrl"]) for url in response.json()["data"]["redditorInfoByName"]["profile"]["socialLinks"]]
