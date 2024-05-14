from __future__ import annotations

import os

from danboorutools.logical.sessions import ScraperResponse, Session


class CircleMsSession(Session):
    def request(self, *args, **kwargs) -> ScraperResponse:
        kwargs.setdefault("cookies", {".ASPXAUTH": os.environ["CIRCLE_MS_ASPXAUTH_COOKIE"]})
        return super().request(*args, **kwargs)
