from __future__ import annotations

import datetime
import inspect
from functools import cached_property, lru_cache
from importlib import import_module
from typing import TYPE_CHECKING, Generic, TypeVar

from danboorutools import logger, settings
from danboorutools.logical.sessions import Session
from danboorutools.models.has_posts import FoundKnownPost, HasPosts

if TYPE_CHECKING:
    from collections.abc import Iterator

feeds: list[type[Feed]] = []


class Feed(HasPosts):  # pylint: disable=abstract-method
    session = Session()

    quit_early_page = 3
    max_post_age = datetime.timedelta(days=14)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[]"

    @property
    def pathable_name(self) -> str:
        return f"Feed.{self.__class__.__name__}"

    @staticmethod
    @lru_cache
    def get_all_feeds() -> list[type[Feed]]:
        feed_folder = settings.BASE_FOLDER / "danboorutools" / "logical" / "feeds"
        for _file in feed_folder.glob("*.py"):
            if "__" not in _file.stem:
                import_module(f"danboorutools.logical.feeds.{_file.stem}")
        return feeds

    def __init_subclass__(cls, *args, **kwargs) -> None:
        if cls.__name__.startswith("_"):
            return

        if inspect.getfile(cls) == __file__:
            return

        feeds.append(cls)

    @cached_property
    def site_name(self) -> str:
        current_module = self.__module__
        subfolder, submodule = current_module.rsplit(".", 1)
        if not subfolder.endswith("danboorutools.logical.feeds"):
            raise NotImplementedError("Site name unknown")
        if not submodule:
            raise NotImplementedError("Site name unknown")
        return submodule

    @property
    def normalized_url(self) -> str:
        raise NotImplementedError(self)


ArtistTypeVar = TypeVar("ArtistTypeVar")

PostDataVar = TypeVar("PostDataVar")


class FeedWithSeparateArtists(Feed, Generic[ArtistTypeVar, PostDataVar]):
    quit_early_page = 1

    def _extract_all_posts(self) -> None:
        collected_artists = self._extract_artists()
        for index, artist in enumerate(collected_artists):
            logger.info(f"\nAt artist {index+1} of {len(collected_artists)}: <e>{artist}</e>.")
            try:
                self.__artist_subloop(artist)
            except FoundKnownPost:
                logger.info("Reached a previously-seen post. Moving to the next artist...")
                continue

        self._post_scan_hook()

    def __artist_subloop(self, artist: ArtistTypeVar) -> None:
        for page, post_objects in enumerate(self._extract_posts_from_each_artist(artist=artist)):
            logger.info(f"At page {page + 1}...")

            for post_data in post_objects:
                self._process_post(post_data)

            if not self.known_posts and page + 1 >= self.quit_early_page:
                logger.info("Stopping early because it's a first-time scan...")
                return

    def _extract_artists(self) -> list[ArtistTypeVar]:
        raise NotImplementedError(f"{self} hasn't implemented artist extraction.")

    def _post_scan_hook(self) -> None:
        return None

    def _extract_posts_from_each_artist(self, artist: ArtistTypeVar) -> Iterator[list[PostDataVar]]:
        raise NotImplementedError(f"{self} hasn't implemented artist processing.")

    def _extract_posts_from_each_page(self) -> Iterator[list[PostDataVar]]:
        while True:
            raise NotImplementedError("Unused")
