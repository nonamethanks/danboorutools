from __future__ import annotations

import atexit
import datetime
import os
import random
import time
from datetime import UTC
from http.client import RemoteDisconnected
from typing import TYPE_CHECKING

from backoff import constant, on_exception
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from seleniumwire.undetected_chromedriver import Chrome

from danboorutools import logger, settings
from danboorutools.exceptions import NoCookiesForDomainError
from danboorutools.util.misc import load_cookies_for, save_cookies_for

if TYPE_CHECKING:
    from pathlib import Path

    from selenium.webdriver.remote.webelement import WebElement

    from danboorutools.models.url import Url


class Browser(Chrome):
    def __init__(self, use_proxy: bool = True):

        options = Options()

        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-gpu")
        options.add_argument("--single-process")
        options.add_argument("--deny-permission-prompts")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")

        service = Service("/usr/bin/chromedriver")

        if (use_proxy and (proxy_connection_string := os.environ.get("SELENIUM_PROXY_CONNECTION_STRING"))):
            seleniumwire_options = {
                "proxy": {
                    "http": proxy_connection_string,
                    "https": proxy_connection_string,
                    "verify_ssl": False,
                },
            }
            super().__init__(service=service, options=options, seleniumwire_options=seleniumwire_options)

        else:
            super().__init__(service=service, options=options)

        self.cookie_dir = settings.BASE_FOLDER / "cookies"

        self.screenshot_dir = settings.BASE_FOLDER / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True, parents=True)

        self.set_window_size(1920, 1080)
        self.implicitly_wait(5)
        self.set_page_load_timeout(15)

        atexit.register(self.__del__)

    def __del__(self) -> None:
        self.quit()

    def load_cookies(self, domain: str) -> None:
        """Load cookies for a domain."""
        self.delete_all_cookies()
        self.set_cookies(load_cookies_for(domain))

    def set_cookies(self, cookies: list[dict[str, str]]) -> None:
        self.execute_cdp_cmd("Network.enable", {})
        for cookie in cookies:
            self.execute_cdp_cmd("Network.setCookie", cookie)
        self.execute_cdp_cmd("Network.disable", {})

    @on_exception(constant, (TimeoutException, RemoteDisconnected), max_tries=3, interval=1, jitter=None)
    def get(self, url: str | Url) -> None:
        if not isinstance(url, str):
            url = url.normalized_url
        logger.trace(f"Browser GET request made to {url}")
        try:
            return super().get(url)
        except TimeoutException:
            self.quit()
            self.__init__()  # pylint: disable=unnecessary-dunder-call
            raise

    def get_next_sibling(self, element: WebElement) -> WebElement:
        return self.execute_script("return arguments[0].nextElementSibling", element)

    def find_elements_by_text(self,
                              text: str,
                              element: Browser | WebElement | None = None,
                              full_match: bool = True,
                              ) -> list[WebElement]:
        """Find an element based on its text in a page."""
        search_string = f'//*[text()="{text}"]' if full_match else f'//*[contains(text(), "{text}")]'
        element = element or self
        elements = element.find_elements("xpath", search_string)
        return elements

    def attempt_login_with_cookies(self,
                                   domain: str,
                                   verification_url: str,
                                   verification_element: str,
                                   ) -> bool:
        try:
            self.load_cookies(domain)
        except NoCookiesForDomainError:
            logger.debug(f"No cookies exist for domain {domain}.")
            return False

        self.get(verification_url)

        try:
            self.find_element("css selector", verification_element)
        except NoSuchElementException:
            logger.debug(f"Failed to login with cookies for {domain}.")
            return False
        else:
            logger.debug(f"Login with cookies for {domain} successful.")
            return True

    def compile_login_form(self,
                           domain: str,
                           form_url: str,
                           steps: list[dict[str, str]],
                           verification_url: str,
                           verification_element: str,
                           ) -> None:
        self.get(form_url)

        for step in steps:
            submit_element = step.pop("submit")
            for secret_name, secret_selector in step.items():

                try:
                    secret_element = self.find_element("css selector", secret_selector)
                except NoSuchElementException:
                    logger.debug("Login failed.")
                    self.screenshot()
                    raise
                secret_key = f"{domain.upper()}_{secret_name.upper()}"
                logger.debug(f"Browser sending secret {secret_key} to {domain}.")
                secret_element.send_keys(os.environ[secret_key])

            logger.debug("Submitting secrets...")
            self.find_element("css selector", submit_element).click()
            time.sleep(random.randint(2, 5))

        self.get(verification_url)

        try:
            self.find_element("css selector", verification_element)
        except NoSuchElementException:
            logger.debug("Login failed.")
            self.screenshot()
            raise
        else:
            logger.debug("Login successful. Saving cookies...")
            save_cookies_for(domain, self.get_cookies())

    def screenshot(self) -> Path:
        """Take a screenshot of the current page."""
        now_str = datetime.datetime.now(tz=UTC).isoformat(timespec="milliseconds")
        filename = (self.screenshot_dir / f"screenshot_{now_str}.png").resolve()
        self.save_screenshot(filename)
        logger.debug(f"Screenshot saved at {filename}")
        return filename
