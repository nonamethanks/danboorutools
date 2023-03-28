from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING

import ring
from pyrate_limiter import Limiter, RequestRate

from danboorutools.exceptions import NoCookiesForDomainError
from danboorutools.logical.sessions import Session

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class NewgroundsSession(Session):
    feed_html_ratelimiter = Limiter(RequestRate(1, 2))

    @feed_html_ratelimiter.ratelimit("newgrounds_feed_html", delay=True)
    def get_html(self, *args, **kwargs) -> BeautifulSoup:
        self.login()
        resp = self.get(*args, **kwargs)
        html = self._response_as_html(resp)

        if "You're making too many requests. Wait a bit before trying again" in str(html):
            time.sleep(60 * 10)
            return self.get_html(*args, **kwargs)

        if "You must be logged in, and at least 18 years of age to view this content!" in str(html):
            raise NotImplementedError("Not logged in.")

        return html

    @ring.lru()
    def login(self) -> None:
        username = os.environ["NEWGROUNDS_USERNAME"]
        password = os.environ["NEWGROUNDS_PASSWORD"]

        base_url = "https://www.newgrounds.com"

        try:
            self.load_cookies()
        except NoCookiesForDomainError:
            pass

        response = self.get(f"{base_url}/passport")
        html = self._response_as_html(response)
        if html.select_one(f"[alt=\"{username}'s Icon\"]"):
            return

        headers = {"Origin": base_url, "Referer": f"{base_url}/passport"}
        login_url = base_url + html.select_one("form[method='post']")["action"]
        data = {
            "username": username,
            "password": password,
            "remember": "1",
            "login": "1",
        }
        response = self.post(login_url, headers=headers, data=data)
        html = self._response_as_html(response)
        if html.select_one(f"[alt=\"{username}'s Icon\"]"):
            return

        raise NotImplementedError
