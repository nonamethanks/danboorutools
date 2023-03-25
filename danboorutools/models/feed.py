from typing import Generic, TypeVar

from danboorutools import logger
from danboorutools.logical.sessions import Session
from danboorutools.models.has_posts import HasPosts, HasPostsOnJson


class Feed(HasPosts):
    session = Session()

    quit_early_page = 3

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[]"


class JsonFeed(HasPostsOnJson, Feed):  # pylint: disable=abstract-method
    ...


ArtistTypeVar = TypeVar("ArtistTypeVar")


class JsonFeedWithSeparateArtists(JsonFeed, Generic[ArtistTypeVar]):
    quit_early_page = 1

    def _extract_artists(self) -> list[ArtistTypeVar]:
        raise NotImplementedError(f"{self} hasn't implemented artist extraction.")

    def _extract_posts(self) -> None:  # type: ignore[override] # pylint: disable=W0237
        collected_artists = self._extract_artists()
        for index, artist in enumerate(collected_artists):
            logger.info(f"\nAt artist {index+1} of {len(collected_artists)}: <e>{artist}</e>.")
            super()._extract_posts(posts_json_url=self.posts_json_url.format(artist=artist))
