from __future__ import annotations

from typing import TYPE_CHECKING

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel

if TYPE_CHECKING:
    from requests import Response


class FanzaSession(Session):
    def request(self, *args, **kwargs) -> Response:
        kwargs["cookies"] = kwargs.get("cookies", {}) | {"age_check_done": "1"}
        return super().request(*args, **kwargs)

    def book_data(self, book_id: str) -> FanzaBookData:
        response = self.get_json_cached(f"https://book.dmm.co.jp/ajax/bff/content/?shop_name=adult&content_id={book_id}")
        return FanzaBookData(**response)


class FanzaBookData(BaseModel):
    title: str
    author: list[dict[str, str]]
    publisher: dict[str, str]
    synopsis: str
    image_urls: dict[str, str]
