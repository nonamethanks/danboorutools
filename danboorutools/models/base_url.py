from functools import cached_property
from typing import Generic, Self, Type, TypeVar, Sequence

import regex

from danboorutools.models.file import File
from danboorutools.util import get_url_domain
from danboorutools.logical.sessions import Session

UrlSubclass = TypeVar("UrlSubclass", bound="BaseUrl")


class BaseUrl:
    patterns: dict[regex.Pattern, str | None]
    domains: list[str]
    site_name: str

    @classmethod
    def from_string(cls, url: str) -> "BaseUrl":
        from danboorutools.logical.extractors import parse_url  # pylint: disable=import-outside-toplevel
        return parse_url(url)

    @classmethod
    def build(cls, url_type: Type["UrlSubclass"], **properties) -> "UrlSubclass":
        for normalization in url_type.patterns.values():
            if not normalization:
                continue
            if not all(f"{{{p}}}" in normalization for p in properties):
                continue
            url = normalization.format(**properties)
            return url_type(url=url, normalization=normalization, properties=properties)  # type: ignore  # XXX false positive

        raise ValueError(url_type, properties)

    @classmethod
    def match(cls, url: str) -> Self | None:  # type: ignore  # XXX false positive
        url_domain = get_url_domain(url)
        if url_domain not in cls.domains:
            return None

        for pattern, normalization in cls.patterns.items():
            if match := pattern.match(url):
                return cls(url, normalization, match.groupdict())

        return None

    def __init__(self, url: str, normalization: str | None, properties: dict[str, str]):
        if self.__class__ == BaseUrl:
            raise RuntimeError("This abstract class cannot be initialized directly.")

        self.original_url = url
        self.normalization = normalization
        self.properties = properties

    @property
    def normalized_url(self) -> str:
        return self.normalization.format(**self.properties) if self.normalization else self.original_url

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.original_url}]"

    def __repr__(self) -> str:
        return self.__str__()


class BaseAssetUrl(BaseUrl):
    file: File

    def download_file(self, headers: dict | None = None, cookies: dict | None = None) -> None:
        downloaded_file = self.session.download_file(self.normalized_url, headers=headers, cookies=cookies)
        self.file = downloaded_file


GenericAsset = TypeVar("GenericAsset", bound="BaseAssetUrl")
GenericPost = TypeVar("GenericPost", bound="BasePostUrl")
GenericGallery = TypeVar("GenericGallery", bound="BaseGalleryUrl")


class BasePostUrl(BaseUrl, Generic[GenericGallery, GenericAsset]):
    """A post contains multiple files."""
    assets: Sequence[GenericAsset]

    def extract_assets(self) -> None:
        raise NotImplementedError

    @cached_property
    def gallery(self) -> GenericGallery:
        raise NotImplementedError


class BaseGalleryUrl(BaseUrl, Generic[GenericPost]):
    """A gallery contains multiple posts."""
    posts: Sequence[GenericPost]

    def extract_posts(self) -> None:
        raise NotImplementedError
