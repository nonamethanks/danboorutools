import requests


class NoCookiesForDomain(FileNotFoundError):
    """We tried to restore cookies we don't have."""

    def __init__(self, domain: str) -> None:
        self.domain = domain
        message = f"Tried to restore Selenium cookies for {self.domain} but found none."
        super().__init__(message)


class HTTPError(Exception):
    """A request failed somewhere."""

    def __init__(self, response: requests.Response) -> None:
        self.response = response
        self.request = response.request
        self.status_code = self.response.status_code
        super().__init__(self.message)

    @property
    def message(self) -> str:
        return f"The request to {self.request.url} failed with status code {self.status_code}."


class DownloadError(HTTPError):
    """A file download failed with a specific error."""


class EHEntaiRateLimit(HTTPError):
    """E-Hentai is ratelimiting."""

    @property
    def message(self) -> str:
        return f"The request to {self.request.url} failed because of too many downloads."


class DanbooruHTTPError(HTTPError):
    """A danbooru HTTP error."""

    def __init__(self, response: requests.Response, *args, **kwargs) -> None:

        self.json_response = response.json()
        self.error_type = response.json()["error"]
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
