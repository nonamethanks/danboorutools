from __future__ import annotations

from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from danboorutools.models.has_posts import HasPosts


class UnknownUrlError(Exception):
    """The url is unexpectedly unknown"""

    def __init__(self, url: object, parser: type | None = None) -> None:
        message = f"Could not parse url '{url}'"
        if parser:
            message += f" (parser: {parser.__name__})"
        message += "."
        super().__init__(message)


class UnparsableUrlError(Exception):
    """The url is expectedly unknown."""

    def __init__(self, url: object) -> None:
        message = f"The url '{url}' is not parsable."
        super().__init__(message)


class NotAnUrlError(Exception):
    """The url is expectedly unknown."""

    def __init__(self, string: str) -> None:
        message = f"The string '{string}' is not an url."
        super().__init__(message)


class NoCookiesForDomainError(FileNotFoundError):
    """We tried to restore cookies we don't have."""

    def __init__(self, domain: str) -> None:
        self.domain = domain
        message = f"Tried to restore Selenium cookies for {self.domain} but found none."
        super().__init__(message)


class HTTPError(Exception):
    """A request failed somewhere."""
    response: requests.Response | None
    status_code: int | None
    original_url: str | None

    def __init__(self, response: requests.Response | None = None, status_code: int | None = None, original_url: str | None = None) -> None:
        if response is not None:
            self.response = response
            self.original_url = response.request.url
            self.status_code = self.response.status_code
        elif status_code is not None and original_url is not None:
            self.response = None
            self.status_code = status_code
            self.original_url = original_url
        else:
            raise ValueError(response, status_code, original_url)
        super().__init__(self.message)

    @property
    def message(self) -> str:
        return f"The request to {self.original_url} failed with status code {self.status_code}."


class DownloadError(HTTPError):
    """A file download failed with a specific error."""


class DeadUrlError(HTTPError):
    """The URL is dead."""


class EHEntaiRateLimitError(HTTPError):
    """E-Hentai is ratelimiting."""

    @property
    def message(self) -> str:
        return f"The request to {self.original_url} failed because of too many downloads."


class InvalidSkebCredentialsError(HTTPError):
    """Skeb credentials are invalid or expired."""

    @property
    def message(self) -> str:
        return f"The request to {self.original_url} failed because the provided Skeb credentials are invalid or expired."


class DanbooruHTTPError(HTTPError):
    """A danbooru HTTP error."""

    def __init__(self, response: requests.Response, *args, **kwargs) -> None:
        try:
            self.json_response = response.json()
        except requests.exceptions.JSONDecodeError as e:
            if "Rate limit exceeded" in response.text:
                self.json_response = {
                    "error": "RateLimitExceeded",
                    "message": "You're doing that too fast",
                    "backtrace": [],
                }
            else:
                raise NotImplementedError(response.text) from e

        try:
            self.error_type = response.json()["error"]
        except KeyError as e:
            raise NotImplementedError(response.json()) from e
        self.error_message = response.json()["message"]
        self.backtrace = response.json()["backtrace"]
        super().__init__(response, *args, **kwargs)

    @property
    def message(self) -> str:
        msg = f"{self.error_type} - {self.error_message}"
        if self.backtrace:
            msg += "\n    Backtrace:"
            for row in self.backtrace:
                msg += f"\n     {row}"
        return msg


class NoPostsError(Exception):
    """No posts were found when scanning for them."""

    def __init__(self, extractor: HasPosts) -> None:
        super().__init__(f"No posts found when scanning with {extractor}")
