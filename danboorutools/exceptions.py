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

        self.url = url
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
        message = f"Tried to restore cookies for {self.domain} but found none."
        super().__init__(message)


class HTTPError(Exception):
    """A request failed somewhere."""
    response: requests.Response | None
    status_code: int | None
    original_url: str | None

    def __init__(self, response: requests.Response | None = None, status_code: int | None = None, original_url: str | None = None) -> None:
        if response is not None:
            self.response = response
            self.original_url = original_url or response.request.url
            self.status_code = status_code or self.response.status_code
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

    def __reduce__(self):
        return (self.__class__, (self.response, self.status_code, self.original_url))


class DownloadError(HTTPError):
    """A file download failed with a specific error."""


class MaintenanceError(HTTPError):
    """The site is undergoing maintenance."""


class DeadUrlError(HTTPError):
    """The URL is dead."""


class RateLimitError(HTTPError):
    """Got 429."""


class CloudFrontError(HTTPError):
    """Got 403 with cloudfront."""

    @property
    def message(self) -> str:
        return f"The request to {self.original_url} failed because this IP is being blocked by CloudFront. Consider setting a proxy."


class EHEntaiRateLimitError(HTTPError):
    """E-Hentai is ratelimiting."""

    @property
    def message(self) -> str:
        return f"The request to {self.original_url} failed because of too many downloads."


class NotLoggedInError(HTTPError):
    @property
    def message(self) -> str:
        return f"The request to {self.original_url} failed with status code {self.status_code}, probably because we are not logged in."


class JsonNotFoundError(HTTPError):
    """An expected json wasn't found in the html."""

    @property
    def message(self) -> str:
        return f"Pattern not found in url {self.original_url}."


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
            elif "Danbooru is down for maintenance" in response.text:
                self.json_response = {
                    "error": "Downbooru",
                    "message": "Danbooru is down for maintenance",
                    "backtrace": [],
                }
            elif "<center><h1>502 Bad Gateway</h1></center>" in response.text and "<center>cloudflare</center>" in response.text:
                self.json_response = {
                    "error": "BadGatewayError",
                    "message": "Cloudflare might be having issues",
                    "backtrace": ["502 Bad Gateway"],
                }
            else:
                raise NotImplementedError(response.text) from e

        try:
            self.error_type = self.json_response["error"]
        except KeyError as e:
            raise NotImplementedError(response.json()) from e

        self.error_message = self.json_response["message"]
        self.backtrace = self.json_response["backtrace"]
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


class NotAnArtistError(Exception):
    """The user is not an (active) artist."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"The user at {url} is not an (active) artist.")


class DuplicateAssetError(Exception):
    ...
