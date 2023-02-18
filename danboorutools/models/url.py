import re
from collections import defaultdict
from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Callable, DefaultDict, Sequence, TypeVar, final

from bs4 import BeautifulSoup

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


known_url_types: DefaultDict[str, list[type["Url"]]] = defaultdict(list)

UrlSubclass = TypeVar("UrlSubclass", bound="Url")

normalization_pattern = re.compile(r"{(\w+)}")


class Url:
    """A generic URL model."""
    session = Session()  # TODO: implement domain-bound rate limitings

    @classmethod
    def parse(cls, url: "str |  Url") -> "Url":
        if isinstance(url, Url):
            return url
        url_parser = import_parser()
        return url_parser.parse(url) or UnknownUrl(ParsableUrl(url))

    normalization: str | None = None

    @cached_property
    @final
    def normalized_url(self) -> str:
        return self._normalize_from_normalization(**self.__dict__)  \
            or self._normalize_from_properties(**self.__dict__)     \
            or self.original_url.url

    @classmethod  # don't cache me
    def _normalize_from_properties(cls, **url_properties) -> str | None:  # pylint: disable=unused-argument
        return None

    @classmethod  # don't cache me
    @final
    def _normalize_from_normalization(cls, **url_properties) -> str | None:
        if not cls.normalization:
            return None
        assert not any(v is None for v in url_properties.values()), url_properties
        url = cls.normalization.format(**url_properties)
        return url

    @staticmethod
    @lru_cache
    @final
    def build(url_type: type["UrlSubclass"], **url_properties) -> "UrlSubclass":
        """Build an Url from its url properties."""
        normalized_url = url_type._normalize_from_normalization(**url_properties) or url_type._normalize_from_properties(**url_properties)
        if not normalized_url:
            raise ValueError(normalized_url, url_properties)

        instance = url_type(url=ParsableUrl(normalized_url))
        for v_name, v_value in url_properties.items():
            value_type = url_type.__annotations__[v_name]
            assert isinstance(v_value, value_type), f"{v_name} was of type {type(v_value)} instead of {value_type}"
            setattr(instance, v_name, v_value)
        return instance

    def __init__(self, url: ParsableUrl):
        self.original_url = url

    def __str__(self) -> str:
        return f"{self.__class__.__name__}[{self.original_url.url}]"
    __repr__ = __str__

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, type(self)):
            return False

        return __o.normalized_url == self.normalized_url

    def __hash__(self) -> int:  # needed for Ward tests
        return hash(self.__str__())

    @settable_property
    def is_deleted(self) -> bool:
        return self.session.head(self.normalized_url).status_code == 404

    @cached_property
    def html(self) -> "BeautifulSoup":
        return self.session.get_html(self.normalized_url)

########################################################################


class UnknownUrl(Url):
    """An unknown url."""

########################################################################


class InfoUrl(Url):
    """An info url is an url that contains non-asset data, such as related artist urls and names."""
    @property
    def related(self) -> list["Url"]:
        """A list of related urls."""
        raise NotImplementedError

    @property
    def names(self) -> list[str]:
        """A list of artist names, in order of relevance."""
        raise NotImplementedError


########################################################################

class GalleryUrl(Url):
    """A gallery contains multiple posts."""

    @settable_property
    def posts(self) -> Sequence["PostUrl"]:
        raise NotImplementedError


class ArtistUrl(GalleryUrl, InfoUrl, Url):  # pylint: disable=abstract-method
    """An artist url is a gallery but also has other extractable data."""


class ArtistAlbumUrl(GalleryUrl, Url):
    """An artist album is an album belonging to an artist url that contains other posts."""

    @settable_property
    def artist(self) -> ArtistUrl:
        raise NotImplementedError


########################################################################

class PostUrl(Url):
    """A post contains multiple assets."""

    @settable_property
    def gallery(self) -> GalleryUrl:
        raise NotImplementedError

    @settable_property
    def assets(self) -> list["PostAssetUrl"]:
        raise NotImplementedError

    @settable_property
    def created_at(self) -> datetime:
        raise NotImplementedError

    @settable_property
    def score(self) -> int:
        raise NotImplementedError

########################################################################


class AssetUrl(Url):
    """An asset contains a list of files. It's usually a list of a single file, but it can be a zip file with multiple subfiles."""
    @settable_property
    def files(self) -> list[File]:
        downloaded_file = self.session.download_file(self.normalized_url)
        if isinstance(downloaded_file, ArchiveFile):
            return downloaded_file.extracted_files
        else:
            return [downloaded_file]


class PostAssetUrl(AssetUrl, Url):
    @settable_property
    def post(self) -> PostUrl:
        raise NotImplementedError

    @settable_property
    def created_at(self) -> datetime:
        return self.post.created_at


class GalleryAssetUrl(AssetUrl, Url):
    """An asset belonging to a gallery instead of a post (such as a background image)."""
    @settable_property
    def gallery(self) -> PostUrl:
        raise NotImplementedError

########################################################################


class RedirectUrl(Url):
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
def import_parser() -> "UrlParser":
    # pylint: disable=import-outside-toplevel
    from danboorutools.logical.parsers import UrlParser
    return UrlParser()
