from __future__ import annotations

import os
from typing import TYPE_CHECKING

from danboorutools.logical.sessions import Session

if TYPE_CHECKING:
    from requests import Response


class CircleMsSession(Session):
    def request(self, *args, **kwargs) -> Response:
        kwargs.setdefault("cookies", {".ASPXAUTH": os.environ["CIRCLE_MS_ASPXAUTH_COOKIE"]})
        return super().request(*args, **kwargs)
