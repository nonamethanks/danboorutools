import re
from dataclasses import dataclass
from functools import cached_property
from urllib.parse import unquote

from danboorutools.exceptions import UnparsableUrl

url_params_pattern = re.compile(r"(?:\?|\&)?([^=]+)=([^&]+)")


@dataclass
class ParsableUrl:
    raw_url: str

    @cached_property
    def url_data(self) -> dict:
        if "?" in self.raw_url:
            url_without_params, url_params = self.raw_url.rsplit("?", maxsplit=1)
        else:
            url_without_params = self.raw_url
            url_params = None

        [scheme, _, *url_parts] = url_without_params.split("/")
        if scheme not in ("http:", "https:"):
            raise ValueError(self.raw_url)

        hostname = url_parts[0].split(":")[0]
        try:
            subdomain, domain, tld = hostname.rsplit(".", maxsplit=2)
            # Technically wrong for stuff like .co.uk, but then again all tld parsers do other stupid shit
            # like thinking username.carrd.co has "carrd.co" as tld
        except ValueError:
            try:
                domain, tld = hostname.rsplit(".")
            except ValueError as e:
                raise UnparsableUrl(self.raw_url) from e
            subdomain = ""

        url_parts = list(filter(bool, url_parts[1:]))  # faster than list comprehension
        return {
            "scheme": scheme,
            "url_parts": url_parts,
            "hostname": hostname,
            "params": url_params,
            "domain": ".".join([domain, tld]),
            "subdomain": subdomain,
            "url_without_params": url_without_params,
        }

    @property
    def url_without_params(self) -> str:
        return self.url_data["url_without_params"]

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

    @cached_property
    def stem(self) -> str:
        return self.url_parts[-1].rsplit(".", maxsplit=1)[0]

    @cached_property
    def extension(self) -> str:
        return self.url_parts[-1].rsplit(".", maxsplit=1)[1]

    @property
    def scheme(self) -> str:
        return self.url_data["scheme"]

    def __str__(self) -> str:
        return f"ParsableUrl[{self.raw_url}]"
    __repr__ = __str__

    def __hash__(self) -> int:
        return hash(self.__str__())
