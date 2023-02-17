import re
from dataclasses import dataclass
from functools import cached_property, lru_cache
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from pydomainextractor import DomainExtractor

from danboorutools.exceptions import UnknownUrlError, UnparsableUrl, UrlParsingError
from danboorutools.util.misc import class_name_to_string

if TYPE_CHECKING:
    from danboorutools.models.url import Url

parsers: dict[str, type["UrlParser"]] = {}

domain_extractor = DomainExtractor()


url_params_pattern = re.compile(r"(?:\?|\&)?([^=]+)=([^&]+)")


@dataclass
class ParsableUrl:
    url: str

    @cached_property
    def url_data(self) -> dict:
        if "\\u" in self.url:
            self.url = self.url.encode("utf-8").decode("unicode-escape")

        [scheme, _, *url_parts] = self.url.split("/")
        if scheme not in ("http:", "https:"):
            raise ValueError(self.url)

        if "?" in url_parts[-1]:
            url_parts[-1], url_params = url_parts[-1].rsplit("?", maxsplit=1)
        else:
            url_params = None

        hostname = url_parts[0].split(":")[0]
        _data = domain_extractor.extract(hostname)
        url_parts = [u for u in url_parts[1:] if u]

        return {
            "scheme": scheme,
            "url_parts": url_parts,
            "hostname": hostname,
            "params": url_params,
            "domain": ".".join([_data["domain"], _data["suffix"]]),
            "subdomain": _data["subdomain"] or None,
        }

    @property
    def hostname(self) -> str:
        return self.url_data["hostname"]

    @property
    def domain(self) -> str:
        return self.url_data["domain"]

    @property
    def subdomain(self) -> str | None:
        return self.url_data["subdomain"]

    @property
    def url_parts(self) -> list[str]:
        return self.url_data["url_parts"]

    @cached_property
    def params(self) -> dict[str, str]:
        if not self.url_data["params"]:
            return {}
        return dict(url_params_pattern.findall(self.url_data["params"]))

    @property
    def scheme(self) -> str:
        return self.url_data["scheme"]


class UrlParser:
    domains: list[str] = []
    test_cases: dict[type["Url"], list[str]]

    @classmethod
    @lru_cache
    def parse(cls, url: str) -> "Url | None":
        try:
            return cls._parse(url)
        except Exception as e:
            e.add_note(f"Failure on: {url}")
            raise

    @staticmethod
    def _parse(url: str) -> "Url | None":
        parsable_url = ParsableUrl(url)

        parser = parsers.get(parsable_url.domain)
        if not parser:
            return None

        if parsable_url.subdomain in [None, "www"] and not parsable_url.url_parts:
            return None

        try:
            parsed_url = parser.match_url(parsable_url)
        except UnparsableUrl:
            return None

        if not parsed_url:
            raise UnknownUrlError(url, parser)

        for url_property in set(parsed_url.__annotations__) - {"session"}:
            if not hasattr(parsed_url, url_property):
                raise UrlParsingError(parsed_url, url_property)
        return parsed_url

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> "Url | None":
        raise NotImplementedError

    def __init_subclass__(cls) -> None:
        if not cls.domains:
            cls.domains = [class_name_to_string(cls, separator=".").removesuffix(".parser")]
        for domain in cls.domains:
            if domain in parsers:
                raise NotImplementedError(domain, (cls, parsers[domain]))
            parsers[domain] = cls


# pylint: disable=import-outside-toplevel
# Due to circular imports this has to be loaded after Url declaration, in order to trigger __init_subclass__

# autopep8: off

for f in Path(__file__).parent.glob("*.py"):
    if "__" not in f.stem:
        import_module(f".{f.stem}", __package__)

del import_module, Path
# autopep8: on
