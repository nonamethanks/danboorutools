from __future__ import annotations

import os
import time

import ring
from pyrate_limiter import Limiter, RequestRate

from danboorutools.exceptions import NoCookiesForDomainError, NotLoggedInError
from danboorutools.logical.sessions import ScraperResponse, Session


class NewgroundsSession(Session):
    feed_html_ratelimiter = Limiter(RequestRate(1, 2))

    def get(self, *args, **kwargs) -> ScraperResponse:
        if "newgrounds.com" in args[0]:
            self.login()

        with self.feed_html_ratelimiter.ratelimit("newgrounds_feed_html", delay=True):
            response = super().get(*args, **kwargs)

        html = response.html

        if "You're making too many requests. Wait a bit before trying again" in str(html):
            time.sleep(60 * 10)
            return self.get(*args, **kwargs)

        if "You must be logged in, and at least 18 years of age to view this content!" in str(html):
            raise NotLoggedInError(response)

        return response

    @ring.lru()
    def login(self) -> None:
        username = os.environ["NEWGROUNDS_USERNAME"]
        password = os.environ["NEWGROUNDS_PASSWORD"]

        base_url = "https://www.newgrounds.com"

        try:
            self.load_cookies()
        except NoCookiesForDomainError:
            pass

        html = super().get(f"{base_url}/passport").html
        if html.select_one(f"[alt=\"{username}'s Icon\"]"):
            return

        headers = {"Origin": base_url, "Referer": f"{base_url}/passport"}
        assert (acttion_el := html.select_one("form[method='post']"))
        login_url = base_url + acttion_el.attrs["action"]
        data = {
            "username": username,
            "password": password,
            "remember": "1",
            "login": "1",
        }
        html = self.post(login_url, headers=headers, data=data).html
        if html.select_one(f"[alt=\"{username}'s Icon\"]"):
            return

        raise NotImplementedError
