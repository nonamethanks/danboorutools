from __future__ import annotations

import os
from typing import TYPE_CHECKING

import ring

from danboorutools.exceptions import NoCookiesForDomainError
from danboorutools.logical.sessions import Session

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from requests import Response


class NijieSession(Session):
    MAX_CALLS_PER_SECOND = 1

    def get_html(self, *args, **kwargs) -> BeautifulSoup:
        self.login()

        resp = self.get(*args, **kwargs)
        html = self._response_as_html(resp)
        if not html.find("a", string="プロフ設定"):
            raise NotImplementedError("Not logged in.")

        return html

    def request(self, method: str, *args, **kwargs) -> Response:
        kwargs["cookies"] = {"R18": "1"} | kwargs.get("cookies", {})
        return super().request(method, *args, **kwargs)

    @ring.lru()
    def login(self) -> None:
        login_url = "https://nijie.info/login.php"
        try:
            self.load_cookies()
            did_login = False
        except NoCookiesForDomainError:
            email = os.environ["NIJIE_EMAIL"]
            password = os.environ["NIJIE_PASSWORD"]

            data = {
                "email": email,
                "password": password,
                "url": login_url,
                "save": "on",
                "ticket": "",
            }
            self.post(
                "https://nijie.info/login_int.php",
                data=data,
                headers={"Referer": login_url},
            )
            did_login = True

        response = self.get(login_url, skip_cache=True)
        html = self._response_as_html(response)
        if html.find("a", string="プロフ設定"):
            if did_login:
                self.save_cookies("nijie_tok", "NIJIEIJIEID")
            return

        raise NotImplementedError(response)
