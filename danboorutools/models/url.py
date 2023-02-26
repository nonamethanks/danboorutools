from __future__ import annotations

from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Callable, Sequence, TypeVar, final, get_type_hints

from bs4 import BeautifulSoup

from danboorutools.exceptions import UrlIsDeleted
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.logical.sessions import Session
from danboorutools.models.file import ArchiveFile, File
from danboorutools.util.misc import settable_property

if TYPE_CHECKING:
    # https://github.com/python/mypy/issues/5107#issuecomment-529372406
    CachedFunc = TypeVar('CachedFunc', bound=Callable)

    def lru_cache(method: CachedFunc) -> CachedFunc:  # pylint: disable=unused-argument
        ...
else:
    from functools import lru_cache


UrlSubclass = TypeVar("UrlSubclass", bound="Url")


class Url:
    """A generic URL model."""
    session = Session()  # TODO: implement domain-bound rate limitings

    @classmethod
    def parse(cls, url: str | Url) -> Url:
        if isinstance(url, Url):
            return url
        url_parser = import_parser()
        return url_parser.parse(url) or UnknownUrl(ParsableUrl(url))

    @cached_property
    def normalized_url(self) -> str:
        return self.normalize(**self.__dict__) or self.parsed_url.raw_url

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        raise NotImplementedError(f"{cls} hasn't implemented .normalize()")

    @staticmethod
    @lru_cache
    @final
    def build(url_type: type[UrlSubclass], **url_properties) -> UrlSubclass:
        """Build an Url from its url properties."""
        normalized_url = url_type.normalize(**url_properties)
        if not normalized_url:
            raise ValueError(normalized_url, url_properties)

        instance = url_type(url=ParsableUrl(normalized_url))

        type_hints = get_type_hints(url_type)
        for property_name, property_value in url_properties.items():
            value_type = type_hints[property_name]
            assert isinstance(property_value, value_type), f"{property_name} was of type {type(property_value)} instead of {value_type}"
            setattr(instance, property_name, property_value)
        return instance

    def __init__(self, url: ParsableUrl):
        self.parsed_url = url

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.normalized_url}]"
    __repr__ = __str__

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, type(self)):
            return False

        return __o.normalized_url == self.normalized_url

    def __hash__(self) -> int:  # needed for Ward tests
        return hash(self.__str__())

    @settable_property
    def is_deleted(self) -> bool:
        try:
            self.session.head_cached(self.normalized_url)
        except UrlIsDeleted:
            return True
        else:
            return False

    @cached_property
    def html(self) -> BeautifulSoup:
        return self.session.get_html(self.normalized_url)


########################################################################


class UnknownUrl(Url):
    """An unknown url."""

    @classmethod
    def normalize(cls, **kwargs) -> None:
        return None


########################################################################


class InfoUrl(Url):
    """An info url is an url that contains non-asset data, such as related artist urls and names."""
    @property
    def related(self) -> list[Url]:
        """A list of related urls."""
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)

    @property
    def primary_names(self) -> list[str]:
        """A list of artist names usable as tags, in order of relevance."""
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)

    @property
    def secondary_names(self) -> list[str]:
        """A list of artist names usable as qualifiers, in order of relevance."""
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)


########################################################################


class GalleryUrl(Url):
    """A gallery contains multiple posts."""

    @settable_property
    def posts(self) -> Sequence[PostUrl]:
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)


class ArtistUrl(GalleryUrl, InfoUrl, Url):  # pylint: disable=abstract-method
    """An artist url is a gallery but also has other extractable data."""


########################################################################

class ArtistAlbumUrl(GalleryUrl, Url):
    """An artist album is an album belonging to an artist url that contains other posts."""

    @settable_property
    def gallery(self) -> GalleryUrl:
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)


########################################################################


class PostUrl(Url):
    """A post contains multiple assets."""

    @settable_property
    def gallery(self) -> GalleryUrl:
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)

    @settable_property
    def assets(self) -> list[PostAssetUrl]:
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)

    @settable_property
    def created_at(self) -> datetime:
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)

    @settable_property
    def score(self) -> int:
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)


########################################################################


class _AssetUrl(Url):
    """An asset contains a list of files. It's usually a list of a single file, but it can be a zip file with multiple subfiles."""
    @cached_property
    def normalized_url(self) -> str:
        # it doesn't make sense for files to have to implement normalize()
        return self.full_size

    @classmethod
    @final
    def normalize(cls, **kwargs) -> str | None:
        raise ValueError("Asset urls can't be normalized from a set of properties.")

    @property
    def full_size(self) -> str:
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)

    @settable_property
    def files(self) -> list[File]:
        downloaded_file = self.session.download_file(self.normalized_url)
        if isinstance(downloaded_file, ArchiveFile):
            return downloaded_file.extracted_files
        else:
            return [downloaded_file]


class PostAssetUrl(_AssetUrl, Url):
    @settable_property
    def post(self) -> PostUrl:
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)

    @settable_property
    def created_at(self) -> datetime:
        return self.post.created_at


class GalleryAssetUrl(_AssetUrl, Url):
    """An asset belonging to a gallery instead of a post (such as a background image)."""
    @settable_property
    def gallery(self) -> PostUrl:
        raise NotImplementedError(self.__class__, self.parsed_url.raw_url)


########################################################################


class RedirectUrl(Url):  # pylint: disable=abstract-method
    """An url that redirects somewhere else."""
    @cached_property
    def resolved(self) -> Url:
        return self.parse(self.session.unscramble(self.normalized_url))

    @property
    def related(self) -> list[Url]:
        if isinstance(self.resolved, InfoUrl):
            return self.resolved.related
        return []

    @settable_property
    def is_deleted(self) -> bool:
        return self.resolved.is_deleted


if TYPE_CHECKING:
    from danboorutools.logical.parsers import UrlParser


@lru_cache
def import_parser() -> UrlParser:
    # pylint: disable=import-outside-toplevel
    from danboorutools.logical.parsers import UrlParser
    return UrlParser()
