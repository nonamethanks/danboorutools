from __future__ import annotations

import os

from danboorutools.logical.sessions import ScraperResponse, Session


class MixiSession(Session):
    COOKIES = {
        "stamp": os.environ.get("MIXI_STAMP_COOKIE"),
        "session":  os.environ.get("MIXI_SESSION_COOKIE"),
    }

    def request(self, *args, **kwargs) -> ScraperResponse:

        kwargs.setdefault("cookies", self.COOKIES.copy())
        return super().request(*args, **kwargs)
