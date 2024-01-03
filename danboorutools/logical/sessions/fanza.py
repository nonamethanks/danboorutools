from __future__ import annotations

from typing import TYPE_CHECKING

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel

if TYPE_CHECKING:
    from requests import Response

import os


class FanzaSession(Session):
    def request(self, *args, **kwargs) -> Response:
        cookies = {
            "age_check_done": "1",
            "INT_SESID": os.environ["DMM_INT_SESID_COOKIE"],
            "INT_SESID_SECURE": os.environ["DMM_INT_SESID_COOKIE"],
            "secid": os.environ["DMM_SECID_COOKIE"],
            "login_secure_id": os.environ["DMM_SECID_COOKIE"],
            "login_session_id":  os.environ["DMM_LOGIN_SESSION_ID_COOKIE"],
            "ckcy_remedied_check": "ktkrt_argt",
            "check_done_login": "true",
            "i3_opnd": os.environ["DMM_I3_OPND_COOKIE"],
        }
        kwargs["cookies"] = kwargs.get("cookies", {}) | cookies
        return super().request(*args, **kwargs)

    def book_data(self, book_id: str) -> FanzaBookData:
        response = self.get(f"https://book.dmm.co.jp/ajax/bff/content/?shop_name=adult&content_id={book_id}").json()
        return FanzaBookData(**response)


class FanzaBookData(BaseModel):
    title: str
    author: list[dict[str, str]]
    publisher: dict[str, str]
    synopsis: str
    image_urls: dict[str, str]
