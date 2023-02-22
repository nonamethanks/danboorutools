import re
from dataclasses import dataclass
from functools import cached_property
from urllib.parse import unquote

from danboorutools.exceptions import UnparsableUrl

url_params_pattern = re.compile(r"(?:\?|\&)?([^=]+)=([^&]+)")


@dataclass
class ParsableUrl:
    url: str

    @cached_property
    def url_data(self) -> dict:
        if "?" in self.url:
            _url, url_params = self.url.rsplit("?", maxsplit=1)
        else:
            _url = self.url
            url_params = None

        [scheme, _, *url_parts] = _url.split("/")
        if scheme not in ("http:", "https:"):
            raise ValueError(self.url)

        hostname = url_parts[0].split(":")[0]
        try:
            subdomain, domain, tld = hostname.rsplit(".", maxsplit=2)
            # Technically wrong for stuff like .co.uk, but then again all tld parsers do other stupid shit
            # like thinking username.carrd.co has "carrd.co" as tld
        except ValueError:
            try:
                domain, tld = hostname.rsplit(".")
            except ValueError as e:
                raise UnparsableUrl(self.url) from e
            subdomain = ""

        url_parts = list(filter(bool, url_parts[1:]))  # faster than list comprehension
        return {
            "scheme": scheme,
            "url_parts": url_parts,
            "hostname": hostname,
            "params": url_params,
            "domain": ".".join([domain, tld]),
            "subdomain": subdomain,
        }

    @property
    def hostname(self) -> str:
        return self.url_data["hostname"]

    @property
    def domain(self) -> str:
        return self.url_data["domain"]

    @property
    def subdomain(self) -> str:
        return self.url_data["subdomain"]

    @property
    def url_parts(self) -> list[str]:
        return self.url_data["url_parts"]

    @cached_property
    def params(self) -> dict[str, str]:
        if not (params := self.url_data["params"]):
            return {}

        if "%5Cu" in params:
            params = unquote(params)
        if "\\u" in params:
            params = params.encode("utf-8").decode("unicode-escape")

        return dict(url_params_pattern.findall(params))

    @property
    def scheme(self) -> str:
        return self.url_data["scheme"]

    def __str__(self) -> str:
        return f"ParsableUrl[{self.url}]"
    __repr__ = __str__

    def __hash__(self) -> int:
        return hash(self.__str__())
