from __future__ import annotations

import builtins
from functools import cached_property
from typing import TYPE_CHECKING, TypeVar, final

import ring
from backoff import expo, on_exception
from requests.exceptions import ReadTimeout

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.parsable_url import ParsableUrl
from danboorutools.logical.sessions import Session
from danboorutools.models.file import ArchiveFile, File
from danboorutools.models.has_posts import HasPosts

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from bs4 import BeautifulSoup

UrlSubclass = TypeVar("UrlSubclass", bound="Url")


class Url:
    """A generic URL model."""
    session = Session()
    normalizable: bool = True
    normalize_template: str | None = None

    @classmethod
    def parse(cls, url: str | Url) -> Url:
        if isinstance(url, Url):
            return url
        url_parser = import_parser()
        return url_parser.parse(url) or UnknownUrl(ParsableUrl(url))

    @cached_property
    def normalized_url(self) -> str:
        if not self.normalizable:
            return self.parsed_url.raw_url
        return self.normalize(**self.__dict__) or self.parsed_url.raw_url

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if cls.normalize_template:
            try:
                return cls.normalize_template.format(**kwargs)
            except KeyError as e:
                raise KeyError(f"Tried to normalize an url of type {cls.__name__} without passing {e}.") from e
        else:
            raise NotImplementedError(f"{cls} hasn't implemented .normalize()")

    @ring.lru()
    @staticmethod
    @final
    def build(url_type: type[UrlSubclass], **url_properties) -> UrlSubclass:
        """Build an Url from its url properties."""
        if not url_type.normalizable:
            raise NotImplementedError(f"{url_type} is not buildable.")
        normalized_url = url_type.normalize(**url_properties)
        if not normalized_url:
            raise ValueError(normalized_url, url_properties)

        instance = url_type(url=ParsableUrl(normalized_url))

        annotations: dict[str, str] = url_type.__annotations__
        for property_name, property_value in url_properties.items():
            if isinstance(annotation := annotations[property_name], str):  # `from __future__ import annotations` is active
                try:
                    property_types = tuple(getattr(builtins, type_str.strip()) for type_str in annotations[property_name].split("|"))
                except AttributeError as e:  # motherfucker
                    e.add_note(f"{property_name=}, {property_value=}, {annotations[property_name]=}")
                    raise
            else:
                property_types = (annotation,)

            assert isinstance(property_value, property_types), \
                f"{property_name} was of type {type(property_value)} instead of {property_types}"

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

        return __o.normalized_url.__repr__().lower() == self.normalized_url.__repr__().lower()

    def __hash__(self) -> int:  # needed for Ward tests
        return hash(self.__repr__().lower())  # lower() might not be completely true, but frankly the chance of collision is not realistic

    @cached_property
    def is_deleted(self) -> bool:
        try:
            response = self.session.get(self.normalized_url, cached=True)
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
        return self.session.get_html(self.normalized_url)

    @cached_property
    @final
    def artist(self) -> ArtistUrl:
        if isinstance(self, ArtistUrl):
            return self
        elif isinstance(self, PostUrl | ArtistAlbumUrl | GalleryAssetUrl):
            return self.gallery.artist
        elif isinstance(self, PostAssetUrl):
            if hasattr(self, "gallery") and self.gallery:  # old pixiv urls have artist stacc data in them
                return self.gallery
            else:
                return self.post.artist
        elif isinstance(self, RedirectUrl):
            return self.resolved.artist
        else:
            raise NotImplementedError(self, type(self))


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


class GalleryUrl(Url, HasPosts):  # pylint: disable=abstract-method
    """A gallery contains multiple posts."""

    def _register_post(self, post: PostUrl, assets: Sequence[PostAssetUrl | str], created_at: datetime | str | int, score: int) -> None:
        super()._register_post(post, assets, created_at, score)
        post.gallery = self


class ArtistUrl(GalleryUrl, InfoUrl, Url):  # pylint: disable=abstract-method
    """An artist url is a gallery but also has other extractable data."""


########################################################################

class ArtistAlbumUrl(GalleryUrl, Url):
    """An artist album is an album belonging to an artist url that contains other posts."""

    @cached_property
    def gallery(self) -> GalleryUrl:
        raise NotImplementedError(self, "hasn't implemented gallery extraction.")


########################################################################


class PostUrl(Url):
    """A post contains multiple assets."""

    def _register_asset(self, asset: PostAssetUrl | str) -> None:
        if "assets" not in self.__dict__:
            self.assets = []

        if isinstance(asset, str):
            parsed_asset = Url.parse(asset)
            assert isinstance(parsed_asset, PostAssetUrl), parsed_asset
            asset = parsed_asset

        if asset in self.assets:
            raise NotImplementedError(asset, self.assets)

        asset.post = self  # pylint: disable=attribute-defined-outside-init # false positive

        self.assets.append(asset)

    @cached_property
    def assets(self) -> list[PostAssetUrl]:  # pylint: disable=method-hidden
        if "assets" not in self.__dict__:
            self._extract_assets()
        return self.assets

    def _extract_assets(self) -> Sequence[PostAssetUrl] | list[str]:
        raise NotImplementedError(self, "hasn't implemented asset extraction.")

    @cached_property
    def gallery(self) -> GalleryUrl:
        raise NotImplementedError(self, "hasn't implemented gallery extraction.")

    @cached_property
    def created_at(self) -> datetime:
        raise NotImplementedError(self, "hasn't implemented created_at extraction.")

    @cached_property
    def score(self) -> int:
        raise NotImplementedError(self, "hasn't implemented score extraction.")


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
    def normalize(cls, **kwargs) -> str | None:  # noqa: ARG003
        raise ValueError("Asset urls can't be normalized from a set of properties.")

    @property
    def full_size(self) -> str:
        raise NotImplementedError(self, "hasn't implemented full_size extraction.")

    @cached_property
    def is_deleted(self) -> bool:
        try:
            self.session.head(self.normalized_url, cached=True, allow_redirects=True)
        except DeadUrlError:
            return True
        else:
            return False


class PostAssetUrl(_AssetUrl, Url):
    @cached_property
    def post(self) -> PostUrl:
        raise NotImplementedError(self, "hasn't implemented post extraction.")

    @cached_property
    def created_at(self) -> datetime:
        return self.post.created_at


class GalleryAssetUrl(_AssetUrl, Url):
    """An asset belonging to a gallery instead of a post (such as a background image)."""
    @cached_property
    def gallery(self) -> PostUrl:
        raise NotImplementedError(self, "hasn't implemented gallery extraction.")


########################################################################


class RedirectUrl(Url):
    """An url that redirects somewhere else."""
    @cached_property
    @on_exception(expo, ReadTimeout, max_tries=3)
    def resolved(self) -> Url:
        try:
            resolved = self.parse(self.session.unscramble(self.normalized_url))
        except DeadUrlError:
            self.is_deleted = True
            raise

        if resolved == self:
            raise DeadUrlError(status_code=404, original_url=self.normalized_url)

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


if TYPE_CHECKING:
    from danboorutools.logical.parsers import UrlParser


@ring.lru()
def import_parser() -> UrlParser:
    from danboorutools.logical.parsers import UrlParser
    return UrlParser()
