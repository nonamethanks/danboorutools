from __future__ import annotations

from typing import TYPE_CHECKING, final

from danboorutools import logger
from danboorutools.exceptions import NoPostsError
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from danboorutools.models.feed import Feed
    from danboorutools.models.url import GalleryUrl, PostAssetUrl, PostUrl


class HasPosts:
    __collected_posts: list[PostUrl]
    known_posts: set[PostUrl]

    posts_json_url: str
    posts_objects_dig: list[str | int]

    quit_early_page = 0

    @final
    def extract_posts(self, known_posts: list[PostUrl] | None = None) -> list[PostUrl]:
        try:
            self.known_posts |= set(known_posts or [])
        except AttributeError:
            self.known_posts = set(known_posts or [])

        self.__collected_posts = []

        try:
            if self.posts_json_url:
                self._extract_from_json()  # type: ignore[misc]
            else:
                self._extract_from_generic()
        except (Exception, KeyboardInterrupt):
            self.__collected_posts = []
            raise

        logger.info(f"Finished scanning. {len(self.__collected_posts)} {'new ' if self.known_posts else ''}posts found.")

        collected_posts = self.__collected_posts
        self.__collected_posts = []

        self.known_posts |= set(collected_posts)
        return collected_posts

    def _extract_from_json(self: GalleryUrl | Feed) -> None:  # type: ignore[misc]
        """Extract posts from an url."""
        page = 1
        logger.debug(f"Scanning {self} for posts...")
        while True:
            if self.quit_early_page and page > self.quit_early_page:
                logger.debug("Quitting early because it's a first-time scan...")
                return

            json_data = self.session.get_json_cached(self.posts_json_url.format(page=page, self=self))
            post_objects = json_data
            logger.debug(f"At page {page}...")

            for dig_element in self.posts_objects_dig:
                try:
                    post_objects = post_objects[dig_element]
                except KeyError as e:
                    raise NotImplementedError(dig_element, post_objects.keys()) from e

            if not post_objects:
                if page == 1:
                    raise NoPostsError(self)
                else:
                    logger.debug("No more posts found. Aborting...")
                    return

            for post_dict_data in post_objects:
                try:
                    self._process_post_from_json(post_dict_data)
                except EndScan:
                    logger.debug("Reached a previously-seen post. Quitting...")
                    return

            logger.debug(f"{len(self.__collected_posts)} posts collected so far.")
            page += 1

    def _extract_from_generic(self) -> None:
        while True:  # trick to stop pylint from nagging me in child classes
            raise NotImplementedError(self, "hasn't implemented post extraction.")

    def _process_post_from_json(self, post_object: dict) -> None:
        while True:
            raise NotImplementedError(f"{self} hasn't implemented post object processing.")
        raise NotImplementedError(post_object)

    def _register_post(self,
                       post: PostUrl,
                       assets: Sequence[PostAssetUrl],
                       created_at: datetime | str,
                       score: int) -> None:
        if post in self.known_posts:
            raise EndScan(Exception)

        if post in self.__collected_posts:
            raise NotImplementedError

        post.created_at = datetime_from_string(created_at)
        post.score = score

        post._assets = []  # what if revision?
        for asset in assets:
            post._register_asset(asset)

        self.__collected_posts.append(post)


class EndScan(Exception):  # noqa: N818
    pass
