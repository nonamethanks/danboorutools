
from functools import cached_property

from methodtools import lru_cache

from danboorutools.logical.sessions import Session


class EHentaiSession(Session):
    site_name = "ehentai"

    @lru_cache()
    def browser_login(self) -> None:
        verification_url = "https://e-hentai.org/home.php"
        verification_element = ".homebox"

        if self.browser.attempt_login_with_cookies(domain=self.site_name,
                                                   verification_url=verification_url,
                                                   verification_element=verification_element):
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
            json_response = self.post("https://api.e-hentai.org/api.php", json=data).json()
            return json_response["tokenlist"][0]["token"]
        except Exception as e:
            raise NotImplementedError(response.text) from e
