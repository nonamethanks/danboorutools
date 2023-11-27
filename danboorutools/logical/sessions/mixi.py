from __future__ import annotations

import os
from typing import TYPE_CHECKING

from danboorutools.logical.sessions import Session

if TYPE_CHECKING:
    from requests import Response


class MixiSession(Session):
    COOKIES = {
        "stamp": os.environ.get("MIXI_STAMP_COOKIE"),
        "session":  os.environ.get("MIXI_SESSION_COOKIE"),
    }

    def request(self, *args, **kwargs) -> Response:

        kwargs.setdefault("cookies", self.COOKIES.copy())
        return super().request(*args, **kwargs)
