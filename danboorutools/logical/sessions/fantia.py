from __future__ import annotations

import json
import os
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import field_validator

from danboorutools import logger
from danboorutools.logical.sessions import ScraperResponse, Session
from danboorutools.util.misc import BaseModel
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from typing import Literal

    from bs4 import BeautifulSoup


class FantiaSession(Session):
    @property
    def _cookies(self) -> dict:
        return {"_session_id": os.environ["FANTIA_SESSION_ID_COOKIE"]}

    def request(self, *args, **kwargs) -> ScraperResponse:
        kwargs["cookies"] = self._cookies | kwargs.get("cookies", {})
        return super().request(*args, **kwargs)

    def get_feed(self, page: int, content_type: Literal["posts", "products"]) -> dict:
        page_json = self.get(f"https://fantia.jp/api/v1/me/timelines/{content_type}?page={page}&per=24").json()
        return page_json

    def get_post_data(self, post_id: int) -> FantiaPostData:
        post_url = f"https://fantia.jp/posts/{post_id}"
        post_html = self.get(post_url).html
        assert (csrf_el := post_html.select_one("meta[name='csrf-token']"))

        headers = {
            "X-CSRF-Token": csrf_el.attrs["content"],
            "x-requested-with": "XMLHttpRequest",
        }

        api_response = self.get(f"https://fantia.jp/api/v1/posts/{post_id}", headers=headers).json()
        if not api_response.get("post"):
            raise NotImplementedError(f"Could not parse fantia api response for {post_url}: {api_response}")

        return FantiaPostData(**api_response["post"])

    def subscribe(self, fanclub_id: int) -> None:
        plans_url = f"https://fantia.jp/fanclubs/{fanclub_id}/plans"
        plans_page = self.get(plans_url).html
        if self.is_subscribed(plans_page):
            logger.info(f"Already subscribed to fanclub #{fanclub_id}. Skipping.")
            return

        logger.info(f"Proceeding to subscribe to fanclub #{fanclub_id}.")

        plan_descr = plans_page.select_one(".plan [title='Become a fan']")
        subscribe_url = "https://fantia.jp" + plan_descr.attrs["href"]
        auth_token_el = plans_page.select_one("meta[name='csrf-token']")
        headers = {
            "Referer": f"https://fantia.jp/fanclubs/{fanclub_id}/plans",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "method": "_post",
            "authenticity_token": auth_token_el.attrs["content"],
        }

        response = self.post(subscribe_url, data=data, headers=headers)
        assert response.ok, response.status_code

        plans_page = self.get(plans_url, skip_cache=True).html
        assert self.is_subscribed(plans_page)

    def unsubscribe(self, fanclub_id: int) -> None:
        plans_url = f"https://fantia.jp/fanclubs/{fanclub_id}/plans"

        plans_page = self.get(plans_url).html
        if not self.is_subscribed(plans_page):
            logger.info(f"Not subscribed to fanclub #{fanclub_id}. Skipping.")
            return

        logger.info(f"Proceeding to unsubscribe from fanclub #{fanclub_id}.")

        assert (subscribed_plan := plans_page.select_one("[title='Plan withdrawal']")), plans_url
        plan_page = self.get("https://fantia.jp" + subscribed_plan.attrs["href"]).html
        assert (form := plan_page.select_one("form[action^='/mypage/users/plans']"))
        assert (auth_token_el := form.select_one("[name='authenticity_token']"))

        data = {
            "_method": "delete",
            "authenticity_token": auth_token_el.attrs["value"],
            "leave_reason_master_id": 11,
            "reason_body": "",
            "commit": "プランの退会を申請",
        }

        headers = {
            "Referer": f"https://fantia.jp/mypage/users/plans/{fanclub_id}/orders/delete",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        unsubscribe_url = "https://fantia.jp" + form.attrs["action"]

        response = self.post(unsubscribe_url, data=data, headers=headers)
        assert response.ok, response.status_code

        plans_page = self.get(plans_url, skip_cache=True).html
        assert not self.is_subscribed(plans_page)

    def is_subscribed(self, page: BeautifulSoup) -> bool:
        assert (first_plan := page.select_one(".plan"))
        assert (plan_price := first_plan.select_one(".plan-price").text) == "0yen($0.00 USD)/Month", plan_price

        return not bool(first_plan.select_one("[title='Become a fan']"))


class FantiaPostData(BaseModel):
    id: int
    posted_at: datetime
    likes_count: int

    thumb: dict
    post_contents: list[dict]

    fanclub: dict

    @field_validator("posted_at", mode="before")
    @classmethod
    def parse_created_at(cls, value: str) -> datetime:
        return datetime_from_string(value)

    @property
    def assets(self) -> list[str]:
        assets = []

        if self.thumb:
            assets.append(self.thumb["original"])

        for content in self.post_contents:
            if content["visible_status"] != "visible":
                continue

            if content["category"] == "photo_gallery":
                assets += [photo["url"]["original"] for photo in content["post_content_photos"]]
            elif content["category"] == "file":
                assets.append("https://fantia.jp/" + content["download_uri"].strip("/"))
            elif content["category"] == "blog":
                _json = json.loads(content["comment"])
                for subjson in _json["ops"]:
                    if isinstance(subjson["insert"], dict):
                        if "fantiaImage" in subjson["insert"]:
                            image = subjson["insert"]["fantiaImage"]["url"]
                        elif "image" in subjson["insert"]:
                            image = subjson["insert"]["image"]
                        else:
                            raise NotImplementedError(subjson)
                        assert isinstance(image, str), subjson
                        assets.append(image)

            elif content["category"] in ["embed", "text"] and not content["content_type"]:
                pass
            else:
                raise NotImplementedError(content["category"], self.id)
        return assets
