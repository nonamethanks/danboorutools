import atexit
import datetime
import os
import pickle
import random
import time
from pathlib import Path

from loguru import logger
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from danboorutools.exceptions import NoCookiesForDomain


class Browser(Chrome):
    def __init__(self):

        options = Options()

        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--single-process")

        super().__init__("/usr/bin/chromedriver", chrome_options=options)

        self.cookie_dir = Path("cookies")

        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True, parents=True)

        self.set_window_size(1920, 1080)
        self.implicitly_wait(5)
        self.set_page_load_timeout(30)

        atexit.register(self.__del__)

    def __del__(self) -> None:
        self.quit()

    def load_cookies(self, domain: str) -> None:
        """Load cookies for a domain."""
        self.delete_all_cookies()
        self.execute_cdp_cmd('Network.enable', {})
        filename = self.cookie_dir / f"cookies-{domain}.pkl"
        try:
            cookies: list[dict] = pickle.load(filename.open("rb"))
        except FileNotFoundError as e:
            raise NoCookiesForDomain(domain) from e
        for cookie in cookies:
            if "expiry" in cookie:
                cookie["expires"] = cookie["expiry"]
                del cookie["expiry"]
            self.execute_cdp_cmd('Network.setCookie', cookie)
            # self.add_cookie(cookie)
        self.execute_cdp_cmd('Network.disable', {})

    def save_cookies(self, domain: str) -> None:
        """Save cookies for a domain."""
        filename = self.cookie_dir / f"cookies-{domain}.pkl"
        self.cookie_dir.mkdir(exist_ok=True)
        pickle.dump(self.get_cookies(), filename.open("wb+"))

    def get(self, url: str) -> None:
        logger.debug(f"Browser GET request made to {url}")
        return super().get(url)

    def find_elements_by_css_selector(self, css_selector: str) -> list[WebElement]:
        """Replace the deprecated function."""
        return self.find_elements(By.CSS_SELECTOR, css_selector)

    def find_element_by_css_selector(self, css_selector: str) -> WebElement:
        """Replace the deprecated function."""
        return self.find_element(By.CSS_SELECTOR, css_selector)

    def find_elements_by_text(self,
                              text: str,
                              element: "Browser | WebElement | None" = None,
                              full_match: bool = True,
                              ) -> list[WebElement]:
        """Find an element based on its text in a page."""
        if full_match:
            search_string = f"//*[text()='{text}']"
        else:
            search_string = f"//*[contains(text(), '{text}')]"

        element = element or self
        elements = element.find_elements(By.XPATH, search_string)
        return elements

    def attempt_login_with_cookies(self,
                                   domain: str,
                                   verification_url: str,
                                   verification_element: str,
                                   ) -> bool:
        try:
            self.load_cookies(domain)
        except NoCookiesForDomain:
            logger.debug(f"No cookies exist for domain {domain}.")
            return False

        self.get(verification_url)

        try:
            self.find_element_by_css_selector(verification_element)
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
                    secret_element = self.find_element_by_css_selector(secret_selector)
                except NoSuchElementException:
                    logger.debug("Login failed.")
                    self.screenshot()
                    raise
                secret_key = f"{domain.upper()}_{secret_name.upper()}"
                logger.debug(f"Browser sending secret {secret_key} to {domain}.")
                secret_element.send_keys(os.environ[secret_key])

            logger.debug("Submitting secrets...")
            self.find_element_by_css_selector(submit_element).click()
            time.sleep(random.randint(2, 5))

        self.get(verification_url)

        try:
            self.find_element_by_css_selector(verification_element)
        except NoSuchElementException:
            logger.debug("Login failed.")
            self.screenshot()
            raise
        else:
            logger.debug("Login successful. Saving cookies...")
            self.save_cookies(domain)

    def screenshot(self) -> Path:
        """Take a screenshot of the current page."""
        now_str = datetime.datetime.utcnow().isoformat(timespec="milliseconds")
        filename = (self.screenshot_dir / f"screenshot_{now_str}.png").resolve()
        self.save_screenshot(filename)
        logger.debug(f"Screenshot saved at {filename}")
        return filename
