from __future__ import annotations

import inspect
from collections.abc import Iterator
from functools import lru_cache
from importlib import import_module
from pathlib import Path
from typing import Generic, TypeVar

from danboorutools import logger
from danboorutools.logical.sessions import Session
from danboorutools.models.has_posts import FoundKnownPost, HasPosts

feeds: list[type[Feed]] = []


class Feed(HasPosts):  # pylint: disable=abstract-method
    session = Session()

    quit_early_page = 3

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[]"

    @staticmethod
    @lru_cache
    def get_all_feeds() -> list[type[Feed]]:
        feed_folder = Path(__file__).parent.parent / "logical" / "feeds"
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

            if self.quit_early_page and page + 1 >= self.quit_early_page:
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
