import json
from functools import cached_property

from danboorutools.logical.sessions import Session
from danboorutools.util.misc import memoize


class EHentaiSession(Session):
    @memoize
    def browser_login(self) -> None:
        verification_url = "https://e-hentai.org/home.php"
        verification_element = ".homebox"

        if self.browser.attempt_login_with_cookies(domain=self.site_name,
                                                   verification_url=verification_url,
                                                   verification_element=verification_element):
            self.__browser_load_exhentai_cookies()
            return

        self.browser.compile_login_form(
            domain=self.site_name,
            form_url="https://e-hentai.org/bounce_login.php",
            steps=[{
                "username": "[name='UserName']",
                "password": "[name='PassWord']",
                "submit": "[name='ipb_login_submit']",
            }],
            verification_url=verification_url,
            verification_element=verification_element,
        )
        self.__browser_load_exhentai_cookies()

    def __browser_load_exhentai_cookies(self) -> None:
        cookies = self.browser._get_cookies_for("ehentai")
        self.browser.execute_cdp_cmd('Network.enable', {})
        for cookie in cookies:
            cookie["domain"] = ".exhentai.org"
            self.browser.execute_cdp_cmd('Network.setCookie', cookie)
        self.browser.execute_cdp_cmd('Network.disable', {})

    @cached_property
    def browser_cookies(self) -> dict:
        self.browser_login()
        cookies = {}
        for browser_cookie in self.browser.get_cookies():
            cookies[browser_cookie["name"]] = browser_cookie["value"]
        return cookies

    def get_gallery_token_from_page_data(self, gallery_id: int | str, page_token: str, page_number: int | str, **kwargs) -> str:
        # pylint: disable=unused-argument
        data = {
            "method": "gtoken",
            "pagelist": [
                [gallery_id, page_token, page_number]
            ]
        }

        response = self.post("https://api.e-hentai.org/api.php", json=data)

        try:
            json_response = response.json()
            return json_response["tokenlist"][0]["token"]
        except json.JSONDecodeError as e:
            raise NotImplementedError(response.text) from e

    def download_file(self, url, *args, download_dir=None, **kwargs):  # noqa
        kwargs.pop("cookies", None)
        return super().download_file(url, *args, download_dir=download_dir, cookies=self.browser_cookies, **kwargs)
