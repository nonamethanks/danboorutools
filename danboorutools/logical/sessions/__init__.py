import os
import time
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from ratelimit import limits, sleep_and_retry
from requests import Response
from requests import Session as RequestsSession

from danboorutools import logger
from danboorutools.exceptions import DownloadError, HTTPError
from danboorutools.logical.browser import Browser
from danboorutools.models.file import File, FileSubclass
from danboorutools.util.misc import get_url_domain, random_string
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from danboorutools.models.url import Url


class Session(RequestsSession):
    _default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Cache-Control": "no-cache, no-store, no-transform"
    }
    _default_timeout = 2

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.logged_in = False
        if self.__class__ == Session:
            self.site_name = ""
        else:
            self.site_name = self.__class__.__name__.lower().removesuffix("session")  # EHentaiSession -> ehentai

        self.proxied_domains: dict[str, dict] = {}

        for envvar in os.environ:
            if envvar.endswith("_PROXY"):
                proxy = os.environ[envvar]
                domain = envvar.removesuffix("_PROXY").lower().replace("_", ".")
                self.proxied_domains[domain] = {"http": proxy, "https": proxy}
                logger.debug(f"Setting a proxy for all connections to {domain}.")

    @cached_property
    def browser(self) -> Browser:
        return Browser()

    @sleep_and_retry
    @limits(calls=5, period=1)
    def request(self, *args, **kwargs) -> Response:
        method, url, args = args[0], args[1], args[2:]
        if not isinstance(url, str):
            url = url.normalized_url

        url_domain = get_url_domain(url)
        kwargs["proxies"] = self.proxied_domains.get(url_domain)
        kwargs["headers"] = self._default_headers | kwargs.get("headers", {})

        logger.debug(f"{method} request made to {url}")
        return super().request(method, url, *args, **kwargs)

    def download_file(self, url: "str | Url", *args, download_dir: Path | str | None = None, **kwargs) -> FileSubclass:
        tmp_filename = Path("/tmp") / random_string(20)
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

        _file = File.identify(tmp_filename, destination_dir=download_dir, md5_as_filename=True)
        return _file

    def get_html(self, url: "str | Url", *args, **kwargs) -> BeautifulSoup:
        if not isinstance(url, str):
            url = url.normalized_url
        response = self.get(url, *args, **kwargs)
        if not response.ok:
            raise HTTPError(response)
        soup = BeautifulSoup(response.text, "html5lib")
        return soup

    def unscramble(self, url: str) -> str:
        resp = self.head(url, allow_redirects=True)
        if resp.status_code != 200:
            return url
        return resp.url
