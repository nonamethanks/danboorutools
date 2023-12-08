from __future__ import annotations

from functools import lru_cache
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

from danboorutools.exceptions import UnknownUrlError, UnparsableUrlError
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.util.misc import class_name_to_string

if TYPE_CHECKING:
    from danboorutools.models.url import UnsupportedUrl, Url

parsers: dict[str, type[UrlParser]] = {}

UNSUPPORTED_DOMAINS = (
    "amebaownd.com",
    "artmug.kr",  # not worth it, looks like a terrible site to implement
    "coocan.jp",
    "discord.gg",  # way too much of a pain in the ass
    "kakao.com",  # korean chat app?
    "itch.io",
    "mbsp.jp",
    "nobody.jp",
    "pixnet.net",
    "ribbon.to",
    "starfree.jp",
    "webclap.com",
    "webnode.jp",
    "wixsite.com",
    "whitesnow.jp",
    "wordpress.com",
)


class UrlParser:
    domains: tuple[str, ...] = ()

    @staticmethod
    @lru_cache
    def setup_subclasses() -> None:
        for _file in (Path(__file__).parent / "parsers").glob("*.py"):
            if "__" not in _file.stem:
                import_module(f"danboorutools.logical.parsers.{_file.stem}")

    def __init_subclass__(cls) -> None:
        if not cls.domains:
            cls.domains = (class_name_to_string(cls, separator=".").removesuffix(".parser"), )
        for domain in cls.domains:
            if domain in parsers:
                raise NotImplementedError(domain, (cls, parsers[domain]))
            parsers[domain] = cls

    @classmethod
    @lru_cache
    def parse(cls, url: str) -> Url:
        cls.setup_subclasses()
        try:
            parsed = cls._parse(url)
        except Exception as e:
            e.add_note(f"Failure on: {url}")
            raise
        if parsed:
            return parsed

        from danboorutools.models.url import UnknownUrl
        return UnknownUrl(parsed_url=ParsableUrl(url))

    @staticmethod
    def _parse(url: str) -> Url | None:
        parsable_url = ParsableUrl(url)
        parser = parsers.get(parsable_url.domain.lower())
        if not parser:
            return None

        if parsable_url.is_base_url:
            return None

        try:
            parsed_url = parser.match_url(parsable_url)
        except UnparsableUrlError:
            return None

        if not parsed_url:
            raise UnknownUrlError(url, parser)

        return parsed_url

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Url | None:
        raise NotImplementedError(parsable_url)


class UnsupportedParser(UrlParser):
    domains = UNSUPPORTED_DOMAINS

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> UnsupportedUrl | None:
        if parsable_url.domain in cls.domains:
            from danboorutools.models.url import UnsupportedUrl
            return UnsupportedUrl(parsed_url=parsable_url)
        else:
            return None
