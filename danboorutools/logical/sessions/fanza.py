from __future__ import annotations

from requests import Response

from danboorutools.logical.sessions import Session


class FanzaSession(Session):
    def request(self, *args, **kwargs) -> Response:
        kwargs["cookies"] = kwargs.get("cookies", {}) | {"age_check_done": "1"}
        return super().request(*args, **kwargs)
