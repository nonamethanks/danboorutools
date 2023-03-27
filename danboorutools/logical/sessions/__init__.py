from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import warnings
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Self
from urllib.parse import urlencode

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from cloudscraper import CloudScraper as _CloudScraper
from cloudscraper.exceptions import CloudflareChallengeError
from pyrate_limiter.limiter import Limiter, RequestRate
from requests.exceptions import ConnectionError as RequestsConnectionError

from danboorutools import logger
from danboorutools.exceptions import DeadUrlError, DownloadError, HTTPError
from danboorutools.logical.browser import Browser
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.models.file import File, FileSubclass
from danboorutools.util.misc import load_cookies_for, memoize, random_string, save_cookies_for
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from requests import Response

    from danboorutools.models.url import Url


_session_cache: dict[type[Session], Session] = {}


class Session(_CloudScraper):
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Cache-Control": "no-cache, no-store, no-transform",
    }
    DEFAULT_TIMEOUT = 5
    MAX_CALLS_PER_SECOND: int | float = 3

    proxied_domains: dict[str, dict] = {}
    for envvar in os.environ:
        if envvar.endswith("_PROXY"):
            proxy = os.environ[envvar]
            domain = envvar.removesuffix("_PROXY").lower().replace("_", ".")
            proxied_domains[domain] = {"http": proxy, "https": proxy}

    def __new__(cls, *args, **kwargs) -> Self:
        if not (new_instance := _session_cache.get(cls)):
            new_instance = _session_cache[cls] = super().__new__(cls, *args, **kwargs)
        return new_instance  # type: ignore[return-value] # stfu

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.session_domain = self.__class__.__name__.lower().replace("session", "")  # used in cookie saving

        if self.MAX_CALLS_PER_SECOND < 1:
            interval = 1 / self.MAX_CALLS_PER_SECOND
            max_calls = 1.0
        else:
            max_calls = self.MAX_CALLS_PER_SECOND
            interval = 1
        self.limiter = Limiter(RequestRate(max_calls, interval))  # type: ignore[arg-type]

    @cached_property
    def browser(self) -> Browser:
        return Browser()

    def request(self, *args, **kwargs) -> Response:
        http_method, url, args = args[0], args[1], args[2:]

        if not isinstance(url, str):
            url = url.normalized_url

        url_domain = ParsableUrl(url).domain
        kwargs["headers"] = self.DEFAULT_HEADERS | kwargs.get("headers", {})

        if kwargs.get("params"):
            logger.trace(f"{http_method} request made to {url}?{urlencode(kwargs['params'])}")
        else:
            logger.trace(f"{http_method} request made to {url}")

        kwargs.setdefault("proxies", self.proxied_domains.get(url_domain))
        kwargs.setdefault("timeout", self.DEFAULT_TIMEOUT)

        try:
            with self.limiter.ratelimit(url_domain, delay=True):
                response = super().request(http_method, url, *args, **kwargs)
        except RequestsConnectionError as e:
            e.add_note(f"Method: {http_method}; url: {url}")
            raise
        except CloudflareChallengeError:
            del sys.tracebacklimit  # fucking cloudscraper
            raise

        if response.status_code == 404:
            raise DeadUrlError(response)
        return response

    def download_file(self, url: str | Url, *args, download_dir: Path | str | None = None, **kwargs) -> FileSubclass:

        tmp_filename = Path(tempfile.gettempdir()) / random_string(20)
        if download_dir is not None:
            download_dir = Path(download_dir)

        kwargs["headers"] = self.DEFAULT_HEADERS | kwargs.get("headers", {})

        download_stream = self.get(url, *args, timeout=self.DEFAULT_TIMEOUT, stream=True, **kwargs)  # type: ignore[arg-type]
        if not download_stream.ok:
            raise DownloadError(download_stream)

        tmp_filename.parent.mkdir(parents=True, exist_ok=True)
        with tmp_filename.open("wb") as dest_buffer:
            for chunk in download_stream.iter_content(chunk_size=1024 * 1024 * 10):
                if chunk:  # filter out keep-alive new chunks
                    dest_buffer.write(chunk)

        if source_time := download_stream.headers.get("last-modified"):
            # Set modification time based on the source. This is useful when downloading files
            # from sources that do not have an easily available timestamp
            unix_time = time.mktime(datetime_from_string(source_time).timetuple())
            os.utime(tmp_filename, (unix_time, unix_time))

        return File.identify(tmp_filename, destination_dir=download_dir, md5_as_filename=True)

    def get_html(self, url: str | Url, *args, cached: bool = True, **kwargs) -> BeautifulSoup:
        if not isinstance(url, str):
            url = url.normalized_url

        method = self.get_cached if cached else self.get
        response = method(url, *args, **kwargs)

        return self._response_as_html(response)

    def _response_as_html(self, response: Response) -> BeautifulSoup:
        if not response.ok:
            raise HTTPError(response)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XMLParsedAsHTMLWarning)
            return BeautifulSoup(response.text, "html5lib")

    def get_json(self, *args, **kwargs) -> dict:
        response = self.get(*args, **kwargs)
        return self._try_json_response(response)

    def get_json_cached(self, *args, **kwargs) -> dict:
        response = self.get_cached(*args, **kwargs)
        return self._try_json_response(response)

    @memoize
    def get_cached(self, *args, **kwargs) -> Response:
        return self.get(*args, **kwargs)

    @memoize
    def head_cached(self, *args, **kwargs) -> Response:
        return self.head(*args, **kwargs)

    @staticmethod
    def _try_json_response(response: Response) -> dict:
        try:
            return response.json()
        except json.JSONDecodeError as e:
            print(response.text)  # noqa: T201
            if not response.ok:
                raise HTTPError(response) from e
            else:
                raise

    def unscramble(self, url: str) -> str:
        resp = self.head_cached(url, allow_redirects=True)
        if resp.status_code != 200:
            return url
        return resp.url

    @cached_property
    def browser_cookies(self) -> dict:
        self.browser_login()
        cookies = {}
        for browser_cookie in self.browser.get_cookies():
            cookies[browser_cookie["name"]] = browser_cookie["value"]
        return cookies

    def browser_login(self) -> None:
        while True:
            raise NotImplementedError(self)

    def save_cookies(self, *cookies: str) -> None:
        to_save = [
            {
                "name": cookie_name,
                "value": self.cookies[cookie_name],
            }
            for cookie_name in cookies
        ]
        save_cookies_for(self.session_domain, cookies=to_save)

    def load_cookies(self) -> None:
        """Load cookies for a domain."""
        for cookie in load_cookies_for(self.session_domain):
            self.cookies.set(**cookie)
