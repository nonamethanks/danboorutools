from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel


class BilibiliSession(Session):
    def user_data(self, user_id: int) -> BilibiliUserData:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        }
        params = {
            "mid": user_id,
            "token": "",
            "platform": "web",
            "web_location": 1550101,
            "w_rid": "d9ed27b397af6a7ac0ed0d4356d9d4c5",
            "wts": 1709807239,
            "dm_img_list": "[]",
            "dm_img_str": "V2ViR0wgMS4wIChPcGVuR0wgRVMgMi4wIENocm9taXVtKQ",
            "dm_cover_img_str": "QU5HTEUgKE5WSURJQSwgTlZJRElBIEdlRm9yY2UgUlRYIDQwNzAgKDB4MDAwMDI3ODYpIERpcmVjdDNEMTEgdnNfNV8wIHBzXzVfMCwgRDNEMTEpR29vZ2xlIEluYy4gKE5WSURJQS",
            "dm_img_inter": '{"ds":[],"wh":[7085,8235,47],"of":[205,410,205]}',
        }
        user_data_resp = self.get(
            "https://api.bilibili.com/x/space/wbi/acc/info",
            params=params,
            headers=headers,
        )
        user_data = user_data_resp.json()
        if user_data.get("message") == "风控校验失败":
            raise NotImplementedError(f"Bilibili risk verification failed for {user_data_resp.request.url}. Update the parameters.")

        return BilibiliUserData(**user_data["data"])


class BilibiliUserData(BaseModel):
    mid: int
    name: str
