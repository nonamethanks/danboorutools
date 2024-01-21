from __future__ import annotations

import os

import ring

from danboorutools import logger
from danboorutools.exceptions import NoCookiesForDomainError
from danboorutools.logical.sessions import ScraperResponse, Session


class NijieSession(Session):
    MAX_CALLS_PER_SECOND = 1

    def request(self, method: str, *args, **kwargs) -> ScraperResponse:
        kwargs["cookies"] = {"R18": "1"} | kwargs.get("cookies", {})
        return super().request(method, *args, **kwargs)

    @ring.lru()
    def login(self) -> None:
        self._cached_request.storage.backend.clear()
        try:
            self.load_cookies()
        except NoCookiesForDomainError:
            response = self._do_login()
        else:
            response = self.get("https://nijie.info/members_update.php", skip_cache=True)
            if self._check_login(response):
                return
            response = self._do_login()

        if not self._check_login(response, save_cookies=True):
            raise NotImplementedError(response.text)

    def _check_login(self, response: ScraperResponse, save_cookies: bool = False) -> bool:
        if response.html.find("a", string="プロフ設定"):
            if save_cookies:
                self.save_cookies("nijie_tok", "NIJIEIJIEID", domain=".nijie.info")
            logger.debug("Confirmed logged in to nijie.")
            return True
        return False

    def _do_login(self) -> ScraperResponse:
        logger.info("Logging into nijie.")
        login_url = "https://nijie.info/age_jump.php?url="
        html = self.get(login_url, skip_cache=True).html

        login_token_el = html.select_one("form[action='/login_int.php'] [name='url']")
        assert login_token_el
        login_token = login_token_el["value"]

        data = {
            "email": os.environ["NIJIE_EMAIL"],
            "password": os.environ["NIJIE_PASSWORD"],
            "url": login_token,
            "ticket": "",
        }
        response = self.post(
            "https://nijie.info/login_int.php",
            data=data,
            headers={"Referer": "https://nijie.info/login.php"},
        )
        return response
