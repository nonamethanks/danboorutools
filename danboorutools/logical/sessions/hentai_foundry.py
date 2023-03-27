from __future__ import annotations

import os
from typing import TYPE_CHECKING

from danboorutools.exceptions import NoCookiesForDomainError
from danboorutools.logical.sessions import Session
from danboorutools.models.url import Url
from danboorutools.util.misc import memoize

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from danboorutools.logical.urls.hentai_foundry import HentaiFoundryPostUrl


class HentaiFoundrySession(Session):
    @memoize
    def get_html(self, url: str | Url, *args, raise_for_filters: bool = False, **kwargs) -> BeautifulSoup:
        if not isinstance(url, str):
            url = url.normalized_url

        try:
            self.load_cookies()
        except NoCookiesForDomainError:
            pass

        response = self.get(url, *args, **kwargs)
        html = self._response_as_html(response)

        if self._filters_are_set(html):
            return html

        if raise_for_filters:
            raise NotImplementedError(url)

        self._set_filters(html)
        return self.get_html(url, *args, raise_for_filters=True, **kwargs)

    def _filters_are_set(self, html: BeautifulSoup) -> bool:
        filter_form = html.select_one("#FilterBox form")
        rating_filters = filter_form.select(".filter_div[class*=' rating_']")
        for rating_filter in rating_filters:
            if dropdown := rating_filter.select_one("select"):
                rating_value = max(dropdown.select("option"), key=lambda el: int(el["value"]))
                if rating_value.get("selected") != "selected":
                    return False
            elif rating_filter.select_one(".ratingCheckbox"):
                if rating_filter.select_one("input.ratingCheckbox").get("checked") != "checked":
                    return False
            else:
                raise NotImplementedError(rating_filter)

        return True

    def _set_filters(self, html: BeautifulSoup) -> None:
        filter_form = html.select_one("#FilterBox form")
        data = {"YII_CSRF_TOKEN": filter_form.select_one("[name='YII_CSRF_TOKEN']")["value"]}

        rating_filters = filter_form.select(".filter_div[class*=' rating_']")
        for rating_filter in rating_filters:
            if dropdown := rating_filter.select_one("select"):
                rating_name = dropdown["id"]
                rating_value = max(dropdown.select("option"), key=lambda el: int(el["value"]))["value"]
            elif rating_filter.select_one(".ratingCheckbox"):
                rating_name = rating_filter.select_one("label")["for"]
                rating_value = 1
            else:
                raise NotImplementedError(rating_filter)
            data[rating_name] = rating_value
        assert len(data) == 20, data

        data["filter_media"] = "A"
        data["filter_order"] = "date_new"
        data["filter_type"] = 0

        resp = self.post("https://www.hentai-foundry.com/site/filters", data=data)
        assert resp.status_code == 200, resp.status_code
        assert not resp.text, resp.text

        self.save_cookies("PHPSESSID")
        self.cookies.clear()
        self.load_cookies()

    @memoize
    def get_feed_posts(self, page: int) -> list[HentaiFoundryPostUrl]:
        username = os.environ["HENTAI_FOUNDRY_USERNAME"]

        url = f"http://www.hentai-foundry.com/users/FaveUsersRecentPictures?username={username}&page={page}&enterAgree=1"

        page_soup = self.get_html(url)

        all_thumbs = page_soup.select("a.thumbLink")
        if not all_thumbs:
            raise NotImplementedError("No posts found. Check cookies.")

        urls = [Url.parse("https://www.hentai-foundry.com" + thumb["href"]) for thumb in all_thumbs]
        return urls  # type: ignore[return-value]
