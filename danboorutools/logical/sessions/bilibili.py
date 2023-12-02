from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel


class BilibiliSession(Session):
    def user_data(self, user_id: int) -> BilibiliUserData:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        }
        user_data = self.get_json(
            f"https://api.bilibili.com/x/space/wbi/acc/info?mid={user_id}", cookies={"buvid3": "lol-lmao-even"}, headers=headers)
        if user_data.get("message") == "风控校验失败":
            raise NotImplementedError(f"Bilibili risk verification failed: {user_data}")

        return BilibiliUserData(**user_data["data"])


class BilibiliUserData(BaseModel):
    mid: int
    name: str
