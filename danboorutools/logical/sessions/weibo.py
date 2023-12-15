from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import field_validator

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import BaseModel, extract_urls_from_string
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from requests import Response


class WeiboSession(Session):
    def request(self, *args, **kwargs) -> Response:
        return super().request(*args, **kwargs)

    def user_data(self, artist_id: int) -> WeiboUserData:
        data_url = f"https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&type=uid&value={artist_id}"

        data = self.get_json(data_url)
        if data.get("msg") == "这里还没有内容":  # user does not exist
            raise DeadUrlError(original_url=data_url, status_code=404)

        return WeiboUserData(**data["data"]["userInfo"])

    def post_data(self, base_62_id: str) -> WeiboPostData:
        url = f"https://m.weibo.cn/status/{base_62_id}"
        try:
            post_json = self.extract_json_from_html(url, pattern=r"\$render_data = \[([\s\S]+)\]\[0\]")
        except ValueError as e:
            if "微博不存在或暂无查看权限!" in self.get_html(url).body.text:
                raise DeadUrlError(original_url=url, status_code=404) from e
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
