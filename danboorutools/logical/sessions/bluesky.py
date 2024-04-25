import os
from functools import cached_property

import ring
from atproto import Client
from atproto_client.models.app.bsky.feed.get_author_feed import Response as FeedResponse

from danboorutools.logical.sessions import Session


class BlueskySession(Session):
    @cached_property
    def api(self) -> Client:
        client = Client(base_url="https://bsky.social")
        client.login(os.environ["BSKY_USERNAME"], os.environ["BSKY_PASSWORD"])
        return client

    def subscribe(self, username: str) -> None:
        did = self.get_did(username)
        self.api.follow(did)

    def unsubscribe(self, username: str) -> None:
        did = self.get_did(username)
        self.api.unfollow(did)

    def get_posts(self, username: str, cursor: str | None = None) -> FeedResponse:
        did = self.get_did(username)
        response = self.api.get_author_feed(actor=did, filter="posts_with_media", cursor=cursor)
        return response

    def get_feed(self, cursor: str | None = None) -> FeedResponse:
        return self.api.get_timeline(cursor=cursor)

    @ring.lru()
    def get_did(self, username: str) -> str:
        return self.api.get_profile(username).did
