from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Sequence, TypeVar

import regex
from bs4 import BeautifulSoup

from danboorutools.logical.sessions import Session
from danboorutools.models.file import ArchiveFile, File
from danboorutools.util.misc import get_url_domain, settable_property

if TYPE_CHECKING:
    # https://github.com/python/mypy/issues/5107#issuecomment-529372406
    CachedFunc = TypeVar('CachedFunc', bound=Callable)

    def lru_cache(method: CachedFunc) -> CachedFunc:  # pylint: disable=unused-argument
        ...
else:
    from functools import lru_cache

known_url_types: list[type["Url"]] = []

UrlSubclass = TypeVar("UrlSubclass", bound="Url")


class Url:
    """A generic URL model."""
    domains: list[str]
    patterns: dict[regex.Pattern[str], str | None]

    session = Session()
    id_name: str | None

    def __init_subclass__(cls):
        if Url not in cls.__bases__:
            known_url_types.append(cls)

    @classmethod
    @lru_cache
    def parse(cls, url: "str | Url") -> "Url":
        """Parse an Url from a string."""
        if isinstance(url, Url):
            return url
        assert isinstance(url, str)
        url_domain = get_url_domain(url)
        for url_strategy in known_url_types:
            if url_domain not in url_strategy.domains:
                continue
            for pattern, normalization in url_strategy.patterns.items():
                if match := pattern.match(url):
                    return url_strategy(url, normalization, match.groupdict())

        return UnknownUrl(url, None, {})

    @classmethod
    @lru_cache
    def build(cls, url_type: type["UrlSubclass"], **url_properties) -> "UrlSubclass":
        """Build an Url from its url properties."""
        for normalization in url_type.patterns.values():
            if not normalization:
                continue
            if not all(f"{{{p}}}" in normalization for p in url_properties):
                continue
            url = normalization.format(**url_properties)
            return url_type(url=url, normalization=normalization, url_properties=url_properties)

        raise ValueError(url_type, url_properties)

    def __init__(self, url: str, normalization: str | None, url_properties: dict[str, str]):
        if self.__class__ == Url:
            raise RuntimeError("This abstract class cannot be initialized directly.")

        self.original_url = url
        self.pattern = normalization
        self.normalized_url = self.pattern.format(**url_properties) if self.pattern else self.original_url
        self.url_properties = url_properties
        self.id = self.url_properties[self.id_name] if self.id_name else None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.normalized_url}]"
    __repr__ = __str__

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, type(self)):
            return False

        return __o.normalized_url == self.normalized_url

    @settable_property
    def is_deleted(self) -> bool:
        return self.session.head(self.normalized_url).status_code == 404

    @cached_property
    def html(self) -> "BeautifulSoup":
        browser = self.session.browser
        if hasattr(self.session, "browser_login"):
            self.session.browser_login()

        if browser.current_url != self.normalized_url:
            browser.get(self.normalized_url)

        return BeautifulSoup(browser.page_source, "html5lib")


class UnknownUrl(Url):
    domains = []
    patterns = {}
    id_name = None


class InfoUrl(Url):  # pylint: disable=abstract-method
    """An info url is an url that contains only non-asset data, such as a stacc pixiv url or a carrd page."""

    @property
    def related(self) -> list["Url"]:
        """A list of related urls."""
        raise NotImplementedError


class AssetUrl(Url):
    """An asset contains a list of files. It's usually a list of a single file, but it can be a zip file with multiple subfiles."""

    @settable_property
    def post(self) -> "PostUrl":
        raise NotImplementedError

    @settable_property
    def created_at(self) -> datetime:
        raise NotImplementedError

    @settable_property
    def files(self) -> list[File]:
        downloaded_file = self.session.download_file(self.normalized_url)
        if isinstance(downloaded_file, ArchiveFile):
            return downloaded_file.extracted_files
        else:
            return [downloaded_file]


GenericAsset = TypeVar("GenericAsset", bound=AssetUrl)


class PostUrl(Url):
    """A post contains multiple assets."""

    @settable_property
    def gallery(self) -> "GalleryUrl":
        raise NotImplementedError

    @settable_property
    def assets(self) -> list[AssetUrl]:
        raise NotImplementedError

    @settable_property
    def created_at(self) -> datetime:
        raise NotImplementedError

    @settable_property
    def score(self) -> int:
        raise NotImplementedError


class GalleryUrl(Url):
    """A gallery contains multiple posts."""

    @settable_property
    def posts(self) -> Sequence[PostUrl]:
        raise NotImplementedError


class ArtistUrl(GalleryUrl, Url):
    """An artist url is a gallery that also has extractable data."""

    @property
    def names(self) -> list[str]:
        """A list of artist names, in order of relevance."""
        raise NotImplementedError

    @property
    def related(self) -> list["Url"]:
        """A list of related urls."""
        raise NotImplementedError


def init_url_subclasses() -> None:
    # Due to circular imports this has to be loaded after Url declaration, in order to trigger __init_subclass__
    # pylint: disable=import-outside-toplevel,unused-import
    import danboorutools.logical.strategies.ehentai  # noqa


init_url_subclasses()
