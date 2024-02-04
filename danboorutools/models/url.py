from __future__ import annotations

from functools import cached_property, lru_cache
from typing import TYPE_CHECKING, Generic, Self, TypeVar, final

from backoff import expo, on_exception
from requests.exceptions import ReadTimeout

from danboorutools.exceptions import DeadUrlError, DuplicateAssetError, UnknownUrlError
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.logical.sessions import Session
from danboorutools.logical.url_parser import UrlParser
from danboorutools.models.file import ArchiveFile, File
from danboorutools.models.has_posts import HasPosts
from danboorutools.util.misc import PseudoDataclass

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from bs4 import BeautifulSoup

UrlSubclass = TypeVar("UrlSubclass", bound="Url")


class Url(metaclass=PseudoDataclass):
    """A generic URL model."""
    session = Session()
    normalizable = True
    normalize_template = ""

    parsed_url: ParsableUrl

    def __init__(self, /, parsed_url: ParsableUrl, **url_properties):
        self.parsed_url = parsed_url
        self.url_properties = url_properties
        for property_name, property_value in url_properties.items():
            setattr(self, property_name, property_value)

    @property
    def pathable_name(self) -> str:
        prop_string = ".".join(f"{key}:{value.__class__.__name__}:{value}" for key, value in self.url_properties.items())
        return f"Url.{self.__class__.__name__}.{prop_string}"

    @classmethod
    def parse(cls, url: str | Url) -> Url:
        if isinstance(url, Url):
            return url
        return UrlParser.parse(url)

    @cached_property
    def normalized_url(self) -> str:
        if not self.normalizable:
            return self.parsed_url.raw_url
        return self.normalize(**self.__dict__) or self.parsed_url.raw_url

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if not cls.normalize_template:
            raise NotImplementedError(f"{cls} hasn't implemented .normalize()")
        try:
            return cls.normalize_template.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"Tried to normalize an url of type {cls.__name__} without passing {e}.") from e

    @final
    @classmethod
    @lru_cache
    def build(cls, /, **url_properties) -> Self:
        """Build an Url from its url properties."""
        if not cls.normalizable:
            raise NotImplementedError(f"{cls} is not buildable.")
        normalized_url = cls.normalize(**url_properties)
        if not normalized_url:
            raise ValueError(normalized_url, url_properties)
        return cls(parsed_url=ParsableUrl(normalized_url), **url_properties)

    if TYPE_CHECKING:
        # fucking mypy
        @classmethod  # type: ignore[no-redef]
        def build(cls: type[UrlSubclass], /, **url_properties) -> UrlSubclass:  # pylint: disable=E0102,W0613
            # sometimes type checkers really make me want to kill myself
            ...

    def __repr__(self) -> str:
        try:
            return f"{self.__class__.__name__}[{self.normalized_url}]"
        except NotImplementedError:
            return f"{self.__class__.__name__}[{self.parsed_url.raw_url}]"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, type(self)):
            return False

        return __o.normalized_url.__repr__().lower() == self.normalized_url.__repr__().lower()

    def __hash__(self) -> int:  # needed for ring.lru
        return hash(self.__repr__().lower())  # lower() might not be completely true, but frankly the chance of collision is not realistic

    @cached_property
    def is_deleted(self) -> bool:
        try:
            response = self.session.get(self.normalized_url)
        except DeadUrlError:
            return True

        resp_url = ParsableUrl(response.url)
        curr_url = ParsableUrl(self.normalized_url)
        if curr_url.url_parts and resp_url.is_base_url:
            if resp_url.hostname in [curr_url.hostname, curr_url.domain]:
                # "www.site.com/artist" -> "site.com" or "www.site.com"
                return True

            raise NotImplementedError(self, resp_url)

        return False

    @cached_property
    def html(self) -> BeautifulSoup:
        return self.session.get(self.normalized_url).html

    @cached_property
    @final
    def artist(self) -> ArtistUrl:
        if isinstance(self, ArtistUrl):
            return self
        elif isinstance(self, PostUrl | ArtistAlbumUrl | GalleryAssetUrl):
            assert self.gallery
            return self.gallery.artist
        elif isinstance(self, PostAssetUrl):
            if hasattr(self, "gallery") and self.gallery:  # old pixiv urls have artist stacc data in them
                return self.gallery
            else:
                return self.post.artist
        elif isinstance(self, RedirectUrl):
            return self.resolved.artist
        elif isinstance(self, UnknownUrl):
            raise UnknownUrlError(self)
        else:
            raise NotImplementedError(self, type(self))

    @cached_property
    def site_name(self) -> str:
        current_module = self.__module__
        subfolder, submodule = current_module.rsplit(".", 1)
        if not subfolder.endswith("danboorutools.logical.urls"):
            raise NotImplementedError("Site name unknown")
        if not submodule:
            raise NotImplementedError("Site name unknown")
        return submodule


########################################################################


class UnknownUrl(Url):
    """An unknown url."""

    @classmethod
    def normalize(cls, **kwargs) -> None:  # noqa: ARG003
        return None


class UselessUrl(Url):
    """A known, but useless, url."""
    @classmethod
    def normalize(cls, **kwargs) -> None:  # noqa: ARG003
        return None


class UnsupportedUrl(Url):
    """A known url that is not worth implementing individually, such as niche japanese blogs."""
    @classmethod
    def normalize(cls, **kwargs) -> None:  # noqa: ARG003
        return None


########################################################################


class InfoUrl(Url):
    """An info url is an url that contains non-asset data, such as related artist urls and names."""
    @property
    def related(self) -> list[Url]:
        """A list of related urls."""
        raise NotImplementedError(self, "hasn't implemented related URL extraction.")

    @property
    def primary_names(self) -> list[str]:
        """A list of artist names usable as tags, in order of relevance."""
        raise NotImplementedError(self, "hasn't implemented name extraction.")

    @property
    def secondary_names(self) -> list[str]:
        """A list of artist names usable as qualifiers, in order of relevance."""
        raise NotImplementedError(self, "hasn't implemented name extraction.")

    @cached_property
    def is_deleted(self) -> bool:
        if "artist_data" in dir(self):
            try:
                self.artist_data  # type: ignore[attr-defined]
            except DeadUrlError:
                return True
            else:
                return False
        else:
            return super().is_deleted


########################################################################


class _AssetUrl(Url):
    """An asset contains a list of files. It's usually a list of a single file, but it can be a zip file with multiple subfiles."""
    @cached_property
    def files(self) -> list[File]:  # pylint: disable=method-hidden
        if "files" not in self.__dict__:
            self.files = self.extract_files()

        return self.files

    def extract_files(self) -> list[File]:
        downloaded_file = self.session.download_file(self.normalized_url)
        if isinstance(downloaded_file, ArchiveFile):
            return downloaded_file.extracted_files
        else:
            return [downloaded_file]

    @cached_property
    @final
    def normalized_url(self) -> str:
        # it doesn't make sense for files to have to implement normalize()
        return self.full_size

    @classmethod
    @final
    def normalize(cls, **kwargs) -> str | None:  # noqa: ARG003
        raise ValueError("Asset urls can't be normalized from a set of properties.")

    @property
    def full_size(self) -> str:
        raise NotImplementedError(self, "hasn't implemented full_size extraction.")

    @cached_property
    def is_deleted(self) -> bool:
        try:
            self.session.head(self.normalized_url, allow_redirects=True)
        except DeadUrlError:
            return True
        else:
            return False


class PostAssetUrl(_AssetUrl, Url):
    @cached_property
    def post(self) -> PostUrl | None:
        raise NotImplementedError(self, "hasn't implemented post extraction.")


class GalleryAssetUrl(_AssetUrl, Url):
    """An asset belonging to a gallery instead of a post (such as a background image)."""
    @cached_property
    def gallery(self) -> GalleryUrl | None:
        raise NotImplementedError(self, "hasn't implemented gallery extraction.")


########################################################################


TypeVarAsset = TypeVar("TypeVarAsset", bound=PostAssetUrl | GalleryAssetUrl)


class HasAssets(Generic[TypeVarAsset]):

    def _register_asset(self, asset: TypeVarAsset | str, is_deleted: bool | None = None) -> None:
        if "assets" not in self.__dict__:
            self.__dict__["assets"] = []

        assert isinstance(asset, _AssetUrl | str), asset
        if isinstance(asset, str):
            asset = Url.parse(asset)

        if asset in self.assets:
            raise DuplicateAssetError(self, asset, self.assets)

        if is_deleted is not None:
            asset.is_deleted = is_deleted

        self.assets.append(asset)

    @property
    def assets(self) -> Sequence[TypeVarAsset]:
        if "assets" not in self.__dict__:
            assets = self._extract_assets()
            if not assets:
                self.__dict__["assets"] = []
            for asset in assets:
                self._register_asset(asset)
        return self.__dict__["assets"]

    def _extract_assets(self) -> Sequence[TypeVarAsset]:
        raise NotImplementedError(self, "hasn't implemented asset extraction.")


########################################################################


class GalleryUrl(Url, HasPosts, HasAssets[GalleryAssetUrl]):
    """A gallery contains multiple posts."""
    asset_type = GalleryAssetUrl

    def subscribe(self) -> None:
        raise NotImplementedError(self, "hasn't implemented subscription.")

    def _extract_assets(self) -> Sequence[GalleryAssetUrl]:
        raise NotImplementedError(self, "hasn't implemented asset extraction.")


class ArtistUrl(GalleryUrl, InfoUrl):  # pylint: disable=abstract-method
    """An artist url is a gallery but also has other extractable data."""


########################################################################


class PostUrl(Url, HasAssets[PostAssetUrl]):
    """A post contains multiple assets."""
    asset_type = PostAssetUrl

    @cached_property
    def gallery(self) -> GalleryUrl:
        raise NotImplementedError(self, "hasn't implemented gallery extraction.")

    @cached_property
    def created_at(self) -> datetime | None:
        raise NotImplementedError(self, "hasn't implemented created_at extraction.")

    @cached_property
    def score(self) -> int:
        raise NotImplementedError(self, "hasn't implemented score extraction.")


########################################################################


class ArtistAlbumUrl(GalleryUrl, Url):
    """An artist album is an album belonging to an artist url that contains other posts."""

    @cached_property
    def gallery(self) -> GalleryUrl | None:
        raise NotImplementedError(self, "hasn't implemented gallery extraction.")


########################################################################


class RedirectUrl(Url):
    """An url that redirects somewhere else."""
    @cached_property
    @on_exception(expo, ReadTimeout, max_tries=3)
    def resolved(self) -> Url:
        try:
            resp = self.session.get(self.normalized_url, allow_redirects=True)
        except DeadUrlError:
            self.is_deleted = True
            raise

        if (resolved := Url.parse(resp.url)) == self:
            raise DeadUrlError(response=resp)

        return resolved

    @property
    def related(self) -> list[Url]:
        if isinstance(self.resolved, InfoUrl):
            return self.resolved.related
        return []

    @cached_property
    def is_deleted(self) -> bool:
        try:
            return self.resolved.is_deleted
        except DeadUrlError:
            return True


########################################################################

class DeadDomainUrl(Url):
    """An url from a dead site or subsite."""
    @cached_property
    def is_deleted(self) -> bool:
        return True


def parse_list(url_strings: list[str], url_type: type[UrlSubclass]) -> list[UrlSubclass]:
    parsed_urls: list[UrlSubclass] = []
    for url_string in url_strings:
        parsed_url = Url.parse(url_string)
        assert isinstance(parsed_url, url_type), (url_string, parsed_url)
        parsed_urls.append(parsed_url)
    return parsed_urls
