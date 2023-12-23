from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import time
import warnings
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlencode

import ring
from backoff import constant, on_exception
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from cloudscraper import CloudScraper as _CloudScraper
from cloudscraper.exceptions import CloudflareChallengeError
from fake_useragent import UserAgent
from pyrate_limiter.limiter import Limiter
from pyrate_limiter.request_rate import RequestRate
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import ConnectTimeout, ReadTimeout

from danboorutools import logger
from danboorutools.exceptions import CloudFrontError, DeadUrlError, DownloadError, HTTPError, JsonNotFoundError, RateLimitError
from danboorutools.logical.browser import Browser
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.models.file import File, FileSubclass
from danboorutools.util.misc import load_cookies_for, random_string, save_cookies_for
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from collections.abc import Callable

    from requests import Response

    from danboorutools.models.url import Url


class Session(_CloudScraper):
    DISABLE_AUTOMATIC_CACHE = False
    DEFAULT_HEADERS = {
        "User-Agent": UserAgent().chrome,
        "Cache-Control": "no-cache, no-store, no-transform",
    }
    DEFAULT_TIMEOUT = 5
    MAX_CALLS_PER_SECOND: int | float = 3

    @ring.lru()
    def __new__(cls, *args, **kwargs):  # noqa: ARG003
        return super().__new__(cls)

    def __str__(self) -> str:  # needed for ring.lru()
        return f"{self.__class__.__name__}[]"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.proxied_domains: dict[str, dict] = {}
        for envvar in os.environ:
            if envvar.endswith("_PROXY"):
                proxy = os.environ[envvar]
                domain = envvar.removesuffix("_PROXY").lower().replace("_", ".")
                self.proxied_domains[domain] = {"http": proxy, "https": proxy}

        self.session_domain = self.__class__.__name__.removesuffix("Session").removesuffix("Api").lower()  # used in cookie saving

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

    def request(self, method: str, *args, skip_cache: bool | None = None, **kwargs) -> Response:
        if skip_cache is True \
                or (skip_cache is None and self.DISABLE_AUTOMATIC_CACHE)\
                or (method.lower() not in ["get", "head"] and skip_cache is not False):
            # always cache every request by default, but discard the cache if a subsequent call is made that does not want a cached version
            # in theory cache access is slower, but who cares, the limiter will always be the request itself anyway
            self._cached_request.delete(method, *args, **kwargs)
        return self._cached_request(method, *args, **kwargs)

    @ring.lru()
    @on_exception(constant, RateLimitError, max_tries=2, interval=30, jitter=None)
    @on_exception(constant, ReadTimeout, max_tries=3, interval=5, jitter=None)
    @on_exception(constant, RequestsConnectionError, max_tries=3, interval=5, jitter=None)
    def _cached_request(self, http_method: str, url: str | Url, *args, **kwargs) -> Response:
        if not isinstance(url, str):
            url = url.normalized_url

        kwargs["headers"] = self.DEFAULT_HEADERS | kwargs.get("headers", {})

        if kwargs.get("params"):
            logger.trace(f"{http_method} request made to {url}?{urlencode(kwargs['params'])}")
        else:
            logger.trace(f"{http_method} request made to {url}")

        url_domain = ParsableUrl(url).domain
        kwargs.setdefault("proxies", self.proxied_domains.get(url_domain))
        kwargs.setdefault("timeout", self.DEFAULT_TIMEOUT)

        try:
            with self.limiter.ratelimit(url_domain, delay=True):
                response: Response = super().request(http_method, url, *args, **kwargs)
        except ConnectionError as e:
            e.add_note(f"Method: {http_method}; url: {url}")
            raise
        except ConnectTimeout as e:
            raise DeadUrlError(original_url=url, status_code=0) from e
        except RequestsConnectionError as e:
            if "Caused by NameResolutionError" in str(e):
                raise DeadUrlError(original_url=url, status_code=0) from e
            else:
                raise
        except CloudflareChallengeError:
            del sys.tracebacklimit  # fucking cloudscraper
            raise

        if response.status_code == 404:
            raise DeadUrlError(response)
        if response.status_code == 429:
            raise RateLimitError(response)
        if response.status_code == 403 and "The Amazon CloudFront distribution is configured to block" in response.text:
            raise CloudFrontError(response)
        return response

    def download_file(self, url: str | Url, *args, download_dir: Path | str | None = None, **kwargs) -> FileSubclass:

        tmp_filename = Path(tempfile.gettempdir()) / random_string(20)
        if download_dir is not None:
            download_dir = Path(download_dir)

        kwargs["headers"] = self.DEFAULT_HEADERS | kwargs.get("headers", {})

        download_stream = self.get(url, *args, timeout=self.DEFAULT_TIMEOUT, stream=True, **kwargs)
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

    def get_html(self, *args, **kwargs) -> BeautifulSoup:
        response = self.get(*args, **kwargs)
        return self._response_as_html(response)

    def _response_as_html(self, response: Response) -> BeautifulSoup:
        if not response.ok:
            raise HTTPError(response)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XMLParsedAsHTMLWarning)
            try:
                # not .text by default because pages like https://soundcloud.com/user-798138171 don't get parsed correctly at the json part
                decoded_content = response.content.decode("utf-8")
            except UnicodeDecodeError:
                decoded_content = response.text
            return BeautifulSoup(decoded_content, "html5lib")

    def get_json(self, *args, **kwargs) -> dict:
        response = self.get(*args, **kwargs)
        return self._try_json_response(response)

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

    def extract_json_from_html(self,
                               url: str,
                               *args,
                               pattern: str,
                               selector: str | None = None,
                               post_process: Callable[[str], str] | None = None,
                               **kwargs) -> dict:
        response = self.get(url, *args, **kwargs)
        html = self._response_as_html(response)

        if not (elements := html.select(selector or "script")):
            raise ValueError(f"No element with selector {selector or 'script'} found in page.")

        for script in elements:
            if (match := re.search(pattern, script.decode_contents())):
                break
        else:
            raise JsonNotFoundError(response)

        parsable_json = match.groups()[0]
        if post_process:
            parsable_json = post_process(parsable_json)
        try:
            parsed_json = json.loads(parsable_json)
        except json.decoder.JSONDecodeError as e:
            raise NotImplementedError(parsable_json) from e
        return parsed_json

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

    def save_cookies(self, *cookies: str, domain: str | None = None) -> None:
        if not cookies:
            raise ValueError("At least one cookie must be saved.")
        to_save = []
        for cookie_name in cookies:
            saved_cookie = self.cookies.get(cookie_name, domain=domain)
            to_save.append({
                "name": cookie_name,
                "value": saved_cookie,
                "domain": domain if domain else "",
            })
        logger.debug(f"Saving cookies: {', '.join(c['name'] + '=' + c['value'] for c in to_save)}.")
        save_cookies_for(self.session_domain, cookies=to_save)

    def load_cookies(self) -> None:
        """Load cookies for a domain."""
        self.cookies.clear()
        for cookie in load_cookies_for(self.session_domain):
            self.cookies.set(**cookie)

    if TYPE_CHECKING:
        def get(self, *args, **kwargs) -> Response:  # pylint: disable=unused-argument
            ...

        def post(self, *args, **kwargs) -> Response:  # pylint: disable=unused-argument
            ...

        def head(self, *args, **kwargs) -> Response:  # pylint: disable=unused-argument
            ...

        def delete(self, *args, **kwargs) -> Response:  # pylint: disable=unused-argument
            ...
