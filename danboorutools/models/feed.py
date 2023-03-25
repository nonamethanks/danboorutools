from typing import Generic, TypeVar

from danboorutools import logger
from danboorutools.logical.sessions import Session
from danboorutools.models.has_posts import HasPosts, HasPostsOnJson


class Feed(HasPosts):
    session = Session()

    quit_early_page = 3
    validate_existence_of_posts = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[]"


class JsonFeed(HasPostsOnJson, Feed):  # pylint: disable=abstract-method
    ...


ArtistTypeVar = TypeVar("ArtistTypeVar")


class FeedWithSeparateArtists(JsonFeed, Generic[ArtistTypeVar]):
    quit_early_page = 1
    validate_existence_of_posts = False

    def _extract_all_posts(self) -> None:  # type: ignore[override] # pylint: disable=W0237
        collected_artists = self._extract_artists()
        for index, artist in enumerate(collected_artists):
            logger.info(f"\nAt artist {index+1} of {len(collected_artists)}: <e>{artist}</e>.")
            self._extract_posts_from_each_artist(artist=artist)

    def _extract_artists(self) -> list[ArtistTypeVar]:
        raise NotImplementedError(f"{self} hasn't implemented artist extraction.")

    def _extract_posts_from_each_artist(self, artist: ArtistTypeVar) -> None:
        raise NotImplementedError(f"{self} hasn't implemented artist processing.")


class JsonFeedWithSeparateArtists(FeedWithSeparateArtists, JsonFeed, Generic[ArtistTypeVar]):  # pylint: disable=abstract-method
    def _extract_posts_from_each_artist(self, artist: ArtistTypeVar) -> None:
        super(JsonFeed, self)._extract_all_posts(posts_json_url=self.posts_json_url.format(artist=artist))
