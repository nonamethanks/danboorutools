from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel


class BilibiliSession(Session):
    def user_data(self, user_id: int) -> BilibiliUserData:
        user_data = self.get_json(f"https://api.bilibili.com/x/space/wbi/acc/info?mid={user_id}")
        return BilibiliUserData(**user_data["data"])


class BilibiliUserData(BaseModel):
    mid: int
    name: str
