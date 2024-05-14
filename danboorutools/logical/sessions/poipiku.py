

import os

from ring import lru

from danboorutools import logger
from danboorutools.logical.sessions import Session


class PoipikuSession(Session):
    @lru()
    def init_browser(self) -> None:
        self.browser.delete_all_cookies()
        self.browser.set_cookies([
            {"name": "POIPIKU_LK", "value": os.environ["POIPIKU_LK_COOKIE"], "domain": ".poipiku.com"},
            {"name": "POIPIKU_CONTENTS_VIEW_MODE", "value": "1", "domain": ".poipiku.com"},
        ])

    def subscribe(self, user_id: int) -> None:
        self.init_browser()

        browser = self.browser
        browser.get(f"https://poipiku.com/{user_id}/")
        follow_button = browser.find_element("css selector", ".UserInfoCmdFollow")
        if follow_button.text == "★unfollow":
            logger.info("Already subscribed.")
            return

        follow_button.click()
        assert follow_button.text == "★unfollow"

    def unsubscribe(self, user_id: int) -> None:
        self.init_browser()

        browser = self.browser
        browser.get(f"https://poipiku.com/{user_id}/")
        follow_button = browser.find_element("css selector", ".UserInfoCmdFollow")
        if follow_button.text == "☆quiet follow":
            logger.info("Already unsubscribed.")
            return

        follow_button.click()
        assert follow_button.text == "☆quiet follow"
