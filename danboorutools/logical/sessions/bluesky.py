import os
from functools import cached_property

from atproto import Client

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel


class BskySession(Session):
    @cached_property
    def api(self) -> Client:
        client = Client(base_url="https://bsky.social")
        client.login(os.environ["BSKY_USERNAME"], os.environ["BSKY_PASSWORD"])
        return client
