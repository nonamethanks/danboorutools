from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Self, Sequence, TypedDict, TypeVar

import regex
from bs4 import BeautifulSoup

from danboorutools.logical.sessions import Session
from danboorutools.models.file import ArchiveFile, File
from danboorutools.util.misc import get_url_domain

if TYPE_CHECKING:
    # https://github.com/python/mypy/issues/5107#issuecomment-529372406
    CachedFunc = TypeVar('CachedFunc', bound=Callable)

    def lru_cache(method: CachedFunc) -> CachedFunc:  # pylint: disable=unused-argument
        ...
else:
    from functools import lru_cache

known_url_types: list[type["Url"]] = []

UrlSubclass = TypeVar("UrlSubclass", bound="Url")


class ExtractableProperties(TypedDict):
    is_deleted: bool


PropertyReturn = TypeVar('PropertyReturn')


def injectable_property(method: property) -> property:

    @property  # type: ignore[misc]  # may god forgive me for my sins
    def wrapper(self):  # noqa
        assert method.fget
        variable_name = method.fget.__name__
        if (variable_value := getattr(self, f"_{variable_name}", None)) is not None:
            return variable_value
        variable_value = method.fget(self)
        setattr(self, f"_{variable_name}", variable_value)
        return variable_value

    return wrapper  # type: ignore[return-value]

# GenericProperties = TypeVar("GenericProperties", bound="ExtractableProperties")
# class Url(Generic[ExtractableProperties]):


class Url:

    """A generic URL model."""
    domains: list[str]
    patterns: dict[regex.Pattern[str], str | None]
    extractable_properties = list(ExtractableProperties.__annotations__.keys())

    session = Session()

    def __init_subclass__(cls):
        if Url not in cls.__bases__:
            for property_name in cls.extractable_properties:
                method = getattr(cls, property_name)
                setattr(cls, property_name, injectable_property(method))
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

    # def inject(self, url: str | "Url", **extracted_properties: Unpack[ExtractableProperties]) -> "Self":
    #     """Initialize an Url from known extracted properties."""
    #     for key, value in extracted_properties.items():
    #         if value is not None and key in self.extractable_properties:
    #             setattr(self, f"_{key}", value)
    #     return self

    # https://github.com/microsoft/pylance-release/issues/2541
    # TODO: use the above implementation once it's implemented in python 3.12, instead of the hack that follows
    # The above will also make it possible to remove .inject from all subclasses

    def inject(self, *, is_deleted: bool = False, **kwargs) -> "Self":  # type: ignore[valid-type]  # pylint: disable=unused-argument
        """Initialize an Url from known extracted properties."""
        starting_arguments = locals() | kwargs

        for key, value in starting_arguments.items():
            if value is not None and key in self.extractable_properties:
                setattr(self, f"_{key}", value)
        return self

    def __init__(self, url: str, normalization: str | None, url_properties: dict[str, str]):
        if self.__class__ == Url:
            raise RuntimeError("This abstract class cannot be initialized directly.")

        self.original_url = url
        self.normalization = normalization
        self.normalized_url = self.normalization.format(**url_properties) if self.normalization else self.original_url
        self.url_properties = url_properties

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.normalized_url}]"
    __repr__ = __str__

    @property
    def is_deleted(self) -> bool:
        raise NotImplementedError

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

    @property
    def related(self) -> list["Url"]:
        """A list of related urls."""
        return []

    @property
    def is_deleted(self) -> bool:
        return getattr(self, "_is_deleted", False)


class InfoUrl(Url):  # pylint: disable=abstract-method
    """An info url is an url that contains only non-asset data, such as a stacc pixiv url or a carrd page."""

    @property
    def related(self) -> list["Url"]:
        """A list of related urls."""
        raise NotImplementedError


class ExtractableAssetProperties(ExtractableProperties):
    post: "PostUrl"
    created_at: datetime
    files: Sequence[File]


class AssetUrl(Url):
    """An asset contains a list of files. It's usually a list of a single file, but it can be a zip file with multiple subfiles."""

    extractable_properties = list(ExtractableAssetProperties.__annotations__.keys())

    # pylint: disable=unused-argument,arguments-differ
    def inject(self,  # type: ignore[override]
               post: "PostUrl",
               created_at: datetime,
               files: Sequence[File],
               is_deleted: bool = False
               ) -> "Self":  # type: ignore[valid-type]
        _locals = locals().copy()
        _locals.pop("self")
        return super().inject(**_locals)

    @property
    def post(self) -> "PostUrl":
        raise NotImplementedError

    @property
    def created_at(self) -> datetime:
        raise NotImplementedError

    @property
    def files(self) -> list[File]:
        # def download_files(self, headers: dict | None = None, cookies: dict | None = None) -> None:
        downloaded_file = self.session.download_file(self.normalized_url)  # , headers=headers, cookies=cookies)
        if isinstance(downloaded_file, ArchiveFile):
            return downloaded_file.extracted_files
        else:
            return [downloaded_file]

    @property
    def related(self) -> list["Url"]:
        """A list of related urls."""
        return self.post.related


class ExtractablePostProperties(ExtractableProperties):
    gallery: "GalleryUrl"
    assets: Sequence["PostUrl"]
    created_at: datetime
    score: int


class PostUrl(Url):
    """A post contains multiple assets."""
    extractable_properties = list(ExtractablePostProperties.__annotations__.keys())

    # pylint: disable=unused-argument,arguments-differ
    def inject(self,  # type: ignore[override]
               gallery: "GalleryUrl",
               assets: Sequence[AssetUrl],
               created_at: datetime,
               score: int = 0,
               is_deleted: bool = False
               ) -> "Self":  # type: ignore[valid-type]
        _locals = locals().copy()
        _locals.pop("self")
        return super().inject(**_locals)

    @property
    def gallery(self) -> "GalleryUrl":
        raise NotImplementedError

    @property
    def assets(self) -> Sequence[AssetUrl]:
        raise NotImplementedError

    @property
    def created_at(self) -> datetime:
        raise NotImplementedError

    @property
    def score(self) -> int:
        raise NotImplementedError

    @property
    def related(self) -> list["Url"]:
        """A list of related urls."""
        return self.gallery.related


class ExtractableGalleryProperties(ExtractableProperties):
    posts: Sequence[PostUrl]


class GalleryUrl(Url):
    """A gallery contains multiple posts."""
    extractable_properties = list(ExtractableGalleryProperties.__annotations__.keys())

    # pylint: disable=arguments-differ,unused-argument
    def inject(self,  # type: ignore[override]
               posts: Sequence[PostUrl],
               is_deleted: bool = False,
               ) -> "Self":  # type: ignore[valid-type]
        _locals = locals().copy()
        _locals.pop("self")
        return super().inject(**_locals)

    @property
    def posts(self) -> Sequence[PostUrl]:
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
