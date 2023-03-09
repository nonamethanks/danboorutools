from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, TypeVar, final, get_type_hints

from danboorutools.exceptions import UrlIsDeleted
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.logical.sessions import Session
from danboorutools.models.file import ArchiveFile, File
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from collections.abc import Callable

    # https://github.com/python/mypy/issues/5107#issuecomment-529372406
    CachedFunc = TypeVar("CachedFunc", bound=Callable)

    def lru_cache(method: CachedFunc) -> CachedFunc:  # pylint: disable=unused-argument  # noqa: ARG001
        ...

    from datetime import datetime

    from bs4 import BeautifulSoup
else:
    from functools import lru_cache


UrlSubclass = TypeVar("UrlSubclass", bound="Url")


class Url:
    """A generic URL model."""
    session = Session()  # TODO: implement domain-bound rate limitings
    normalize_string: str | None = None

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
        if cls.normalize_string:
            return cls.normalize_string.format(**kwargs)
        else:
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

    def __repr__(self) -> str:
        try:
            return f"{self.__class__.__name__}[{self.normalized_url}]"
        except NotImplementedError:
            return f"{self.__class__.__name__}[{self.parsed_url.raw_url}]"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, type(self)):
            return False

        return __o.normalized_url == self.normalized_url

    def __hash__(self) -> int:  # needed for Ward tests
        return hash(self.__str__())

    @cached_property
    def is_deleted(self) -> bool:
        try:
            self.session.get_cached(self.normalized_url)
        except UrlIsDeleted:
            return True
        else:
            return False

    @cached_property
    def html(self) -> BeautifulSoup:
        return self.session.get_html(self.normalized_url)

    @cached_property
    @final
    def artist(self) -> ArtistUrl:
        if isinstance(self, ArtistUrl):
            return self
        elif isinstance(self, (PostUrl, ArtistAlbumUrl, GalleryAssetUrl)):
            return self.gallery.artist
        elif isinstance(self, PostAssetUrl):
            return self.post.artist
        elif isinstance(self, RedirectUrl):
            return self.resolved.artist
        else:
            raise NotImplementedError(self, type(self))


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
        raise NotImplementedError(self.__class__, "hasn't implemented related URL extraction.")

    @property
    def primary_names(self) -> list[str]:
        """A list of artist names usable as tags, in order of relevance."""
        raise NotImplementedError(self.__class__, "hasn't implemented name extraction.")

    @property
    def secondary_names(self) -> list[str]:
        """A list of artist names usable as qualifiers, in order of relevance."""
        raise NotImplementedError(self.__class__, "hasn't implemented name extraction.")


########################################################################


class GalleryUrl(Url):
    """A gallery contains multiple posts."""
    _posts: list[PostUrl]

    def _register_post(self, post: PostUrl, assets: list[PostAssetUrl], created_at: datetime | str, score: int) -> None:
        if not hasattr(self, "_posts"):
            self._posts = []

        if post in self._posts:
            raise NotImplementedError

        post.created_at = datetime_from_string(created_at)
        post.score = score
        post.gallery = self

        for asset in assets:
            post._register_asset(asset)

        self._posts.append(post)

    @property
    @final
    def posts(self) -> list[PostUrl]:
        if not hasattr(self, "_posts"):
            try:
                # self.extract_posts()
                self._extract_posts()
            except Exception:
                if hasattr(self, "_posts"):
                    del self._posts
                raise
        return self._posts

    # TODO
    # def extract_posts(self) -> None:
    #     try:
    #         self._extract_posts()
    #     except PostAlreadySeen:
    # #     in order to update with revisions, new posts for feeds, etc
    #         return

    def _extract_posts(self) -> None:
        raise NotImplementedError(self.__class__, "hasn't implemented post extraction.")


class ArtistUrl(GalleryUrl, InfoUrl, Url):  # pylint: disable=abstract-method
    """An artist url is a gallery but also has other extractable data."""


########################################################################

class ArtistAlbumUrl(GalleryUrl, Url):
    """An artist album is an album belonging to an artist url that contains other posts."""

    @cached_property
    def gallery(self) -> GalleryUrl:
        raise NotImplementedError(self.__class__, "hasn't implemented gallery extraction.")


########################################################################


class PostUrl(Url):
    """A post contains multiple assets."""
    _assets: list[PostAssetUrl]

    def _register_asset(self, asset: PostAssetUrl | str) -> None:
        if not hasattr(self, "_assets"):
            self._assets = []

        if isinstance(asset, str):
            parsed_asset = Url.parse(asset)
            assert isinstance(parsed_asset, PostAssetUrl), parsed_asset
            asset = parsed_asset

        if asset in self._assets:
            raise NotImplementedError

        asset.post = self

        self._assets.append(asset)

    @property
    @final
    def assets(self) -> list[PostAssetUrl]:
        if not hasattr(self, "_assets"):
            try:
                self._extract_assets()
            except Exception:
                if hasattr(self, "_assets"):
                    del self._assets
                raise
        return self._assets

    def _extract_assets(self) -> None:
        raise NotImplementedError(self.__class__, "hasn't implemented asset extraction.")

    @cached_property
    def gallery(self) -> GalleryUrl:
        raise NotImplementedError(self.__class__, "hasn't implemented gallery extraction.")

    @cached_property
    def created_at(self) -> datetime:
        raise NotImplementedError(self.__class__, "hasn't implemented created_at extraction.")

    @cached_property
    def score(self) -> int:
        raise NotImplementedError(self.__class__, "hasn't implemented score extraction.")


########################################################################


class _AssetUrl(Url):
    """An asset contains a list of files. It's usually a list of a single file, but it can be a zip file with multiple subfiles."""
    _files: list[File]

    @property
    def files(self) -> list[File]:
        if not hasattr(self, "_files"):
            self.extract_files()

        return self._files

    def extract_files(self) -> None:
        downloaded_file = self.session.download_file(self.normalized_url)
        if isinstance(downloaded_file, ArchiveFile):
            self._files = downloaded_file.extracted_files
        else:
            self._files = [downloaded_file]

    @cached_property  # type: ignore[misc]
    @final
    def normalized_url(self) -> str:
        # it doesn't make sense for files to have to implement normalize()
        return self.full_size

    @classmethod
    @final
    def normalize(cls, **kwargs) -> str | None:
        raise ValueError("Asset urls can't be normalized from a set of properties.")

    @property
    def full_size(self) -> str:
        raise NotImplementedError(self.__class__, "hasn't implemented full_size extraction.")

    @cached_property
    def is_deleted(self) -> bool:
        try:
            self.session.head_cached(self.normalized_url, allow_redirects=True)
        except UrlIsDeleted:
            return True
        else:
            return False


class PostAssetUrl(_AssetUrl, Url):
    @cached_property
    def post(self) -> PostUrl:
        raise NotImplementedError(self.__class__, "hasn't implemented post extraction.")

    @cached_property
    def created_at(self) -> datetime:
        return self.post.created_at


class GalleryAssetUrl(_AssetUrl, Url):
    """An asset belonging to a gallery instead of a post (such as a background image)."""
    @cached_property
    def gallery(self) -> PostUrl:
        raise NotImplementedError(self.__class__, "hasn't implemented gallery extraction.")


########################################################################


class RedirectUrl(Url):
    """An url that redirects somewhere else."""
    @cached_property
    def resolved(self) -> Url:
        try:
            return self.parse(self.session.unscramble(self.normalized_url))
        except UrlIsDeleted:
            self.is_deleted = True
            raise

    @property
    def related(self) -> list[Url]:
        if isinstance(self.resolved, InfoUrl):
            return self.resolved.related
        return []

    @cached_property
    def is_deleted(self) -> bool:
        return self.resolved.is_deleted


if TYPE_CHECKING:
    from danboorutools.logical.parsers import UrlParser


@lru_cache
def import_parser() -> UrlParser:
    # pylint: disable=import-outside-toplevel
    from danboorutools.logical.parsers import UrlParser
    return UrlParser()
