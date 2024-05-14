from __future__ import annotations

from datetime import datetime

from pydantic import field_validator

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions import ScraperResponse, Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string
from danboorutools.util.time import datetime_from_string


class WeiboSession(Session):
    def request(self, *args, **kwargs) -> ScraperResponse:
        return super().request(*args, **kwargs)

    def user_data(self, artist_id: int) -> WeiboUserData:
        data_url = f"https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&type=uid&value={artist_id}"

        response = self.get(data_url)
        data = response.json()
        if data.get("msg") == "这里还没有内容":  # user does not exist
            raise DeadUrlError(response=response)

        return WeiboUserData(**data["data"]["userInfo"])

    def post_data(self, base_62_id: str | None = None, long_id: int | None = None) -> WeiboPostData:
        if base_62_id:
            url = f"https://m.weibo.cn/status/{base_62_id}"
        elif long_id:
            url = f"https://m.weibo.cn/detail/{long_id}"
        else:
            raise ValueError("Either base_62_id or long_id must be provided.")

        response = self.get(url)
        try:
            post_json = response.search_json(pattern=r"\$render_data = \[([\s\S]+)\]\[0\]")
        except ValueError as e:
            body = response.html.body.text
            if "微博不存在或暂无查看权限!" in body or "由于博主设置，目前内容暂不可见。" in body or "暂无查看权限" in body:
                raise DeadUrlError(response) from e
            else:
                raise
        return WeiboPostData(**post_json["status"])


class WeiboUserData(BaseModel):
    id: int
    screen_name: str

    description: str

    @property
    def related_urls(self) -> list[Url]:
        urls = [Url.parse(u) for u in extract_urls_from_string(self.description)]

        return list(dict.fromkeys(urls))


class WeiboPostData(BaseModel):
    bid: str  # base 62 id
    mid: int  # long id

    user: WeiboUserData

    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def validate_created_at(cls, value: str) -> datetime:
        return datetime_from_string(value)
