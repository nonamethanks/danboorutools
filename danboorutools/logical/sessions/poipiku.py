import os
from http.client import RemoteDisconnected

from backoff import constant, on_exception
from ring import lru
from selenium.common.exceptions import TimeoutException
from urllib3.exceptions import MaxRetryError

from danboorutools import logger
from danboorutools.logical.sessions import ScraperResponse, Session


class PoipikuSession(Session):
    @lru()
    def init_browser(self) -> None:
        self.browser.delete_all_cookies()
        self.browser.set_cookies([
            {"name": "POIPIKU_LK", "value": os.environ["POIPIKU_LK_COOKIE"], "domain": ".poipiku.com"},
            {"name": "POIPIKU_CONTENTS_VIEW_MODE", "value": "1", "domain": ".poipiku.com"},
        ])

    @on_exception(constant, (TimeoutException, MaxRetryError, RemoteDisconnected), max_tries=3, interval=5, jitter=None)
    def browser_get(self, url: str) -> None:
        self.init_browser()

        try:
            self.browser.get(url)
        except TimeoutException:
            pass

        try:  # check if it's a real timeoutexception or just selenium being retarded
            assert self.browser.current_url
        except (TimeoutException, MaxRetryError):
            self.browser.quit()
            del self.browser
            self.init_browser.storage.backend.clear()
            raise

    def subscribe(self, user_id: int) -> None:
        browser = self.browser
        browser.get(f"https://poipiku.com/{user_id}/")
        follow_button = browser.find_element("css selector", ".UserInfoCmdFollow")
        if follow_button.text == "★unfollow":
            logger.info("Already subscribed.")
            return

        follow_button.click()
        assert follow_button.text == "★unfollow"

    def unsubscribe(self, user_id: int) -> None:
        browser = self.browser
        browser.get(f"https://poipiku.com/{user_id}/")
        follow_button = browser.find_element("css selector", ".UserInfoCmdFollow")
        if follow_button.text == "☆quiet follow":
            logger.info("Already unsubscribed.")
            return

        follow_button.click()
        assert follow_button.text == "☆quiet follow"

    def request(self, *args, **kwargs) -> ScraperResponse:
        headers: dict[str, str] = kwargs.pop("headers", {})
        headers.setdefault("referer", "https://poipiku.com/")
        return super().request(*args, headers=headers, **kwargs)
