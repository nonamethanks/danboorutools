from typing import Generic, Self, TypeVar, Type

import regex

from danboorutools.models.file import File
from danboorutools.util import get_url_domain


class BaseUrl:
    patterns: dict[regex.Pattern, str | None]
    domains: list[str]
    site_name: str

    @classmethod
    def from_string(cls, url: str) -> "BaseUrl":
        from danboorutools.logical.strategies import parse_url  # pylint: disable=import-outside-toplevel
        return parse_url(url)

    @classmethod
    def build(cls, url_type: Type["UrlSubclass"], **properties) -> "UrlSubclass":
        for normalization in url_type.patterns.values():
            if not normalization:
                continue
            if not all(f"{{{p}}}" in normalization for p in properties):
                continue
            url = normalization.format(**properties)
            return url_type(url=url, normalization=normalization, properties=properties)

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


UrlSubclass = TypeVar("UrlSubclass", bound=BaseUrl)


class BaseAssetUrl(BaseUrl):
    file: File


GenericAsset = TypeVar("GenericAsset", bound="BaseAssetUrl")


class BasePostUrl(BaseUrl, Generic[GenericAsset]):
    """A post contains multiple files."""
    assets: list[GenericAsset]

    def extract_assets(self) -> None:
        raise NotImplementedError
        # assets = [self.from_string(url) for url in self._extract_assets()]
        # assert all(isinstance(asset, BaseAssetUrl) for asset in assets)
        # self.assets = assets


GenericPost = TypeVar("GenericPost", bound="BasePostUrl")


class BaseGalleryUrl(BaseUrl, Generic[GenericPost]):
    """A gallery contains multiple posts."""
    posts: list[GenericPost]

    def extract_posts(self) -> None:
        raise NotImplementedError
        # posts = [self.from_string(url) for url in self._extract_posts()]
        # assert all(isinstance(post, BasePostUrl) for post in posts)
        # self.posts = posts
