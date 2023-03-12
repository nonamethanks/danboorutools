from __future__ import annotations

import json
import os
import tempfile
import time
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from cloudscraper import CloudScraper as _CloudScraper
from ratelimit import limits, sleep_and_retry
from requests.exceptions import ConnectionError as RequestsConnectionError

from danboorutools import logger
from danboorutools.exceptions import DownloadError, HTTPError, UrlIsDeleted
from danboorutools.logical.browser import Browser
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.models.file import File, FileSubclass
from danboorutools.util.misc import memoize, random_string
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from requests import Response

    from danboorutools.models.url import Url


class Session(_CloudScraper):
    _default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Cache-Control": "no-cache, no-store, no-transform",
    }
    _default_timeout = 5

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.proxied_domains: dict[str, dict] = {}

        for envvar in os.environ:
            if envvar.endswith("_PROXY"):
                proxy = os.environ[envvar]
                domain = envvar.removesuffix("_PROXY").lower().replace("_", ".")
                self.proxied_domains[domain] = {"http": proxy, "https": proxy}

    @cached_property
    def browser(self) -> Browser:
        return Browser()

    @sleep_and_retry
    @limits(calls=5, period=1)
    def request(self, *args, **kwargs) -> Response:
        http_method, url, args = args[0], args[1], args[2:]

        if not isinstance(url, str):
            url = url.normalized_url

        url_domain = ParsableUrl(url).domain
        kwargs["proxies"] = self.proxied_domains.get(url_domain)
        kwargs["headers"] = self._default_headers | kwargs.get("headers", {})

        if kwargs.get("params"):
            logger.trace(f"{http_method} request made to {url}?{urlencode(kwargs['params'])}")
        else:
            logger.trace(f"{http_method} request made to {url}")

        kwargs.setdefault("timeout", self._default_timeout)

        try:
            response = super().request(http_method, url, *args, **kwargs)
        except RequestsConnectionError as e:
            e.add_note(f"Method: {http_method}; url: {url}")
            raise

        if response.status_code == 404:
            raise UrlIsDeleted(response)
        return response

    def download_file(self, url: str | Url, *args, download_dir: Path | str | None = None, **kwargs) -> FileSubclass:

        tmp_filename = Path(tempfile.gettempdir()) / random_string(20)
        if download_dir is not None:
            download_dir = Path(download_dir)

        kwargs["headers"] = self._default_headers | kwargs.get("headers", {})

        download_stream = self.get(url, *args, timeout=self._default_timeout, stream=True, **kwargs)  # type: ignore[arg-type]
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

    def get_html(self, url: str | Url, *args, **kwargs) -> BeautifulSoup:
        if not isinstance(url, str):
            url = url.normalized_url
        response = self.get_cached(url, *args, **kwargs)
        if not response.ok:
            raise HTTPError(response)
        return BeautifulSoup(response.text, "html5lib")

    def get_json(self, *args, **kwargs) -> dict:
        response = self.request("GET", *args, **kwargs)
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
