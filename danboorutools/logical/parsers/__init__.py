from functools import lru_cache
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from danboorutools.exceptions import UnknownUrlError, UnparsableUrl, UrlParsingError
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.util.misc import class_name_to_string

if TYPE_CHECKING:
    from danboorutools.models.url import Url

parsers: dict[str, type["UrlParser"]] = {}


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
