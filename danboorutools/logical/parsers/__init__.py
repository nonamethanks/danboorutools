from __future__ import annotations

from functools import lru_cache
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from danboorutools.exceptions import UnknownUrlError, UnparsableUrl
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.util.misc import class_name_to_string

if TYPE_CHECKING:
    from danboorutools.models.url import Url

parsers: dict[str, type[UrlParser]] = {}


class UrlParser:
    domains: list[str] = []

    @classmethod
    @lru_cache
    def parse(cls, url: str) -> Url | None:
        try:
            return cls._parse(url)
        except Exception as e:
            e.add_note(f"Failure on: {url}")
            raise

    @staticmethod
    def _parse(url: str) -> Url | None:
        parsable_url = ParsableUrl(url)
        parser = parsers.get(parsable_url.domain)
        if not parser:
            return None

        if parsable_url.is_base_url:
            return None

        try:
            parsed_url = parser.match_url(parsable_url)
        except UnparsableUrl:
            return None

        if not parsed_url:
            raise UnknownUrlError(url, parser)

        return parsed_url

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Url | None:
        raise NotImplementedError

    def __init_subclass__(cls) -> None:
        if not cls.domains:
            cls.domains = [class_name_to_string(cls, separator=".").removesuffix(".parser")]
        for domain in cls.domains:
            if domain in parsers:
                raise NotImplementedError(domain, (cls, parsers[domain]))
            parsers[domain] = cls


for f in Path(__file__).parent.glob("*.py"):
    if "__" not in f.stem:
        import_module(f".{f.stem}", __package__)


# from danboorutools.exceptions import UnparsableUrl
# from danboorutools.logical.extractors.Xxx import XxxArtistUrl, XxxImageUrl, XxxPostUrl, XxxUrl
# from danboorutools.logical.parsers import ParsableUrl, UrlParser


# class XxxXxxParser(UrlParser):
#     @classmethod
#     def match_url(cls, parsable_url: ParsableUrl) -> XxxUrl | None:
#         match parsable_url.url_parts:
#             case _, _, var:
#                 instance = XxxArtistUrl(parsable_url)
#                 instance.var = var
#             case _:
#                 return None

#         return instance
