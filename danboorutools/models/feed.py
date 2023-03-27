from collections.abc import Iterator
from typing import Generic, TypeVar

from danboorutools import logger
from danboorutools.logical.sessions import Session
from danboorutools.models.has_posts import FoundKnownPost, HasPosts


class Feed(HasPosts):  # pylint: disable=abstract-method
    session = Session()

    quit_early_page = 3

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[]"


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

            logger.info(f"{len(self._collected_posts)} posts collected so far.")

            if self.quit_early_page and page >= self.quit_early_page:
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
