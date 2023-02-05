import os
import time
from functools import cached_property
from pathlib import Path

from ratelimit import limits, sleep_and_retry
from requests import Response
from requests import Session as RequestsSession

from danboorutools import logger
from danboorutools.exceptions import DownloadError
from danboorutools.logical.browser import Browser
from danboorutools.models.file import File, FileSubclass
from danboorutools.util import random_string
from danboorutools.util.time import timestamp_from_string


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

    @cached_property
    def browser(self) -> Browser:
        return Browser()

    @sleep_and_retry
    @limits(calls=5, period=1)
    def request(self, *args, **kwargs) -> Response:
        logger.debug(f"{args[0]} request made to {args[1]}")
        return super().request(*args, **kwargs)

    def download_file(self, url: str, *args, download_dir: Path | str | None = None, **kwargs) -> FileSubclass:
        tmp_filename = Path("/tmp") / random_string(20)
        if download_dir is not None:
            download_dir = Path(download_dir)

        kwargs["headers"] = kwargs.get("headers") or {} | self._default_headers

        download_stream = self.get(url, *args, timeout=self._default_timeout, stream=True, **kwargs)
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
            unix_time = time.mktime(timestamp_from_string(source_time).timetuple())
            os.utime(tmp_filename, (unix_time, unix_time))

        _file = File.identify(tmp_filename, destination_dir=download_dir, md5_as_filename=True)
        return _file
