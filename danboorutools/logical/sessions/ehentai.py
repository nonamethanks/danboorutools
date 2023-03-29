from __future__ import annotations

from typing import TYPE_CHECKING

import ring
from bs4 import BeautifulSoup

from danboorutools.logical.sessions import Session

if TYPE_CHECKING:
    from requests import Response

    from danboorutools.models.url import Url


class EHentaiSession(Session):
    def request(self, *args, **kwargs) -> Response:
        return super().request(*args, cookies=self.browser_cookies, **kwargs)

    @ring.lru()
    def browser_login(self) -> None:
        verification_url = "https://e-hentai.org/home.php"
        verification_element = ".homebox"

        if self.browser.attempt_login_with_cookies(domain="ehentai",
                                                   verification_url=verification_url,
                                                   verification_element=verification_element):
            return

        self.browser.compile_login_form(
            domain="ehentai",
            form_url="https://e-hentai.org/bounce_login.php",
            steps=[{
                "username": "[name='UserName']",
                "password": "[name='PassWord']",
                "submit": "[name='ipb_login_submit']",
            }],
            verification_url=verification_url,
            verification_element=verification_element,
        )

    def get_html(self, url: str | Url, *args, **kwargs) -> BeautifulSoup:
        self.browser_login()
        if not isinstance(url, str):
            url = url.normalized_url

        self.head(url)
        if self.browser.current_url != url:
            self.browser.get(url)

        return BeautifulSoup(self.browser.page_source, "html5lib")

    @ring.lru()
    def get_gallery_token_from_page_data(self, gallery_id: int | str, page_token: str, page_number: int | str) -> str:
        data = {
            "method": "gtoken",
            "pagelist": [
                [gallery_id, page_token, page_number],
            ],
        }

        response = self.post("https://api.e-hentai.org/api.php", json=data)
        json_response = self._try_json_response(response)

        try:
            return json_response["tokenlist"][0]["token"]
        except KeyError as e:
            e.add_note(f"Response: {json_response}")
            raise

    def download_file(self, url, *args, download_dir=None, **kwargs):
        kwargs.pop("cookies", None)
        return super().download_file(url, *args, download_dir=download_dir, **kwargs)
