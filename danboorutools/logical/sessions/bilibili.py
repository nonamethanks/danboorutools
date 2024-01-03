from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel


class BilibiliSession(Session):
    def user_data(self, user_id: int) -> BilibiliUserData:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        params = {
            "mid": user_id,
            "token": "",
            "platform": "web",
            "web_location": 1550101,
            "w_rid": "32289ba23bfdf801c576934db527f3e9",
            "wts": 1703443487,
        }
        user_data = self.get(
            "https://api.bilibili.com/x/space/wbi/acc/info",
            params=params,
            headers=headers,
        ).json()
        if user_data.get("message") == "风控校验失败":
            raise NotImplementedError(f"Bilibili risk verification failed: {user_data}")

        return BilibiliUserData(**user_data["data"])


class BilibiliUserData(BaseModel):
    mid: int
    name: str
