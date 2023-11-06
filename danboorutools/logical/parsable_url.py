from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property
from urllib.parse import unquote

from danboorutools.exceptions import NotAnUrlError

url_query_pattern = re.compile(r"(?:\?|\&(?:amp;)*)?([^=]+)=([^&]+)")
# note: some sites garble and double-encode ampersands


@dataclass
class ParsableUrl:
    raw_url: str
    ctld = {
        "co.uk",
        "co.jp", "ne.jp", "or.jp",
        "com.tw",
    }

    @cached_property
    def url_data(self) -> dict:
        if "?" in self.raw_url:
            url_without_query, _, url_query = self.raw_url.partition("?")
        else:
            url_without_query = self.raw_url
            url_query = None

        try:
            [scheme, _, hostname, *url_parts] = url_without_query.split("/")
        except ValueError as e:
            raise NotAnUrlError(self.raw_url) from e

        if scheme not in ("http:", "https:"):
            raise NotAnUrlError(self.raw_url)

        hostname = hostname.split(":")[0]
        *subdomains, domain, tld = hostname.split(".")
        if f"{domain}.{tld}" in self.ctld:
            subdomains, domain, tld = subdomains[:-1], subdomains[-1], f"{domain}.{tld}"

        subdomain = ".".join(subdomains)

        url_parts = list(filter(bool, url_parts))  # faster than list comprehension
        return {
            "scheme": scheme,
            "url_parts": url_parts,
            "hostname": hostname,
            "query": url_query,
            "domain": ".".join([domain, tld]),
            "tld": tld,
            "subdomain": subdomain,
            "url_without_query": url_without_query,
        }

    @property
    def url_without_query(self) -> str:
        return self.url_data["url_without_query"]

    @property
    def hostname(self) -> str:
        return self.url_data["hostname"]

    @property
    def domain(self) -> str:
        return self.url_data["domain"]

    @property
    def tld(self) -> str:
        return self.url_data["tld"]

    @property
    def subdomain(self) -> str:
        return self.url_data["subdomain"]

    @property
    def url_parts(self) -> list[str]:
        return self.url_data["url_parts"]

    @property
    def path(self) -> str:
        return self.raw_url.removeprefix(f"{self.scheme}//{self.hostname}")

    @cached_property
    def query(self) -> dict[str, str]:
        if not (query := self.url_data["query"]):
            return {}

        if "%" in query:
            query = unquote(query)
        if "\\u" in query:
            query = query.encode("utf-8").decode("unicode-escape")

        return dict(url_query_pattern.findall(query))

    @cached_property
    def filename(self) -> str:
        return self.url_parts[-1]

    @cached_property
    def stem(self) -> str:
        return self.filename.split(".")[0]

    @cached_property
    def extension(self) -> str:
        try:
            return self.filename.partition(".")[-1]
        except IndexError:
            return ""

    @property
    def scheme(self) -> str:
        return self.url_data["scheme"]

    @property
    def is_base_url(self) -> bool:
        return not self.url_parts and self.subdomain in ("", "www")

    def __str__(self) -> str:
        return f"ParsableUrl[{self.raw_url}]"
    __repr__ = __str__

    def __hash__(self) -> int:
        return hash(self.__str__())

    def without(self, *parts: str) -> ParsableUrl:
        string = f"{self.scheme}//{self.hostname}/" + "/".join(u for u in self.url_parts if u not in parts)

        if self.query:
            string += "?" + "&".join(f"{k}={v}" for k, v in self.query.items())

        return ParsableUrl(string)
