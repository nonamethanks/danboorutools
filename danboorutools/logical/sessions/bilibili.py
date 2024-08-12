from __future__ import annotations

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import BaseModel


class BilibiliSession(Session):
    def user_data(self, user_id: int) -> BilibiliUserData:
        params = {
            "mid": user_id,
            "token": "",
            "platform": "web",
            "web_location": 1550101,
            "dm_img_list": "[]",
            "dm_img_str": "V2ViR0wgMS4wIChPcGVuR0wgRVMgMi4wIENocm9taXVtKQ",
            "dm_cover_img_str": "QU5HTEUgKE5WSURJQSwgTlZJRElBIEdlRm9yY2UgUlRYIDQwNzAgKDB4MDAwMDI3ODYpIERpcmVjdDNEMTEgdnNfNV8wIHBzXzVfMCwgRDNEMTEpR29vZ2xlIEluYy4gKE5WSURJQS",
            "dm_img_inter": '{"ds":[],"wh":[7753,8986,25],"of":[303,606,303]}',
            "w_rid": "e0704f0a5fb2fd600801d1833f352c13",
            "wts": 1723464010,
        }
        user_data_resp = self.get(
            "https://api.bilibili.com/x/space/wbi/acc/info",
            params=params,
        )
        user_data = user_data_resp.json()
        if user_data.get("message") == "风控校验失败":
            raise NotImplementedError(f"Bilibili risk verification failed for {user_data_resp.request.url}. Update the parameters.")

        return BilibiliUserData(**user_data["data"])


class BilibiliUserData(BaseModel):
    mid: int
    name: str
