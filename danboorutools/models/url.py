from functools import cached_property
from typing import Generic, Sequence, TypeVar

import regex

from danboorutools.logical.sessions import Session
from danboorutools.models.file import ArchiveFile, File
from danboorutools.util import get_url_domain

url_types: list[type["Url"]] = []

UrlSubclass = TypeVar("UrlSubclass", bound="Url")


class Url:
    """A generic URL model."""
    domains: list[str]
    patterns: dict[regex.Pattern[str], str | None]

    session = Session()
    site_name = session.site_name

    @classmethod
    def parse(cls, url: str) -> "Url":
        url_domain = get_url_domain(url)

        for url_strategy in url_types:
            if url_domain not in url_strategy.domains:
                continue

            for pattern, normalization in cls.patterns.items():
                if match := pattern.match(url):
                    return cls(url, normalization, match.groupdict())

        return UnknownUrl(url, None, {})

    @classmethod
    def build(cls, url_type: type["UrlSubclass"], **properties) -> "UrlSubclass":
        for normalization in url_type.patterns.values():
            if not normalization:
                continue
            if not all(f"{{{p}}}" in normalization for p in properties):
                continue
            url = normalization.format(**properties)
            return url_type(url=url, normalization=normalization, properties=properties)

        raise ValueError(url_type, properties)

    def __init_subclass__(cls):
        if cls.__name__ in ["AssetUrl", "PostUrl", "GalleryUrl"]:
            return
        url_types.append(cls)

    def __init__(self, url: str, normalization: str | None, properties: dict[str, str]):
        if self.__class__ == Url:
            raise RuntimeError("This abstract class cannot be initialized directly.")

        self.original_url = url
        self.normalization = normalization
        self.properties = properties

    @property
    def normalized_url(self) -> str:
        return self.normalization.format(**self.properties) if self.normalization else self.original_url

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.original_url}]"
    __repr__ = __str__


class UnknownUrl(Url):
    domains = []
    patterns = {}


GenericAsset = TypeVar("GenericAsset", bound="AssetUrl")
GenericPost = TypeVar("GenericPost", bound="PostUrl")
GenericGallery = TypeVar("GenericGallery", bound="GalleryUrl")


class AssetUrl(Url):
    """An asset contains a list of files. It's usually a list of a single file, but it can be a zip file with multiple subfiles."""
    files: Sequence[File]

    def download_files(self, headers: dict | None = None, cookies: dict | None = None) -> None:
        downloaded_file = self.session.download_file(self.normalized_url, headers=headers, cookies=cookies)
        if isinstance(downloaded_file, ArchiveFile):
            self.files = downloaded_file.extracted_files
        else:
            self.files = [downloaded_file]


class PostUrl(Generic[GenericGallery, GenericAsset]):
    """A post contains multiple assets."""
    assets: Sequence[GenericAsset]

    def extract_assets(self) -> None:
        raise NotImplementedError

    @cached_property
    def gallery(self) -> GenericGallery:
        raise NotImplementedError


class GalleryUrl(Generic[GenericPost]):
    """A gallery contains multiple posts."""
    posts: Sequence[GenericPost]

    def extract_posts(self) -> None:
        raise NotImplementedError
