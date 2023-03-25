from __future__ import annotations

from typing import TYPE_CHECKING, final

from danboorutools import logger
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from danboorutools.models.feed import Feed
    from danboorutools.models.url import GalleryUrl, PostAssetUrl, PostUrl


class HasPosts:
    _collected_posts: list[PostUrl]
    known_posts: set[PostUrl]

    quit_early_page = 0
    validate_existence_of_posts = False

    @final
    def extract_posts(self, known_posts: list[PostUrl] | None = None) -> list[PostUrl]:
        try:
            self.known_posts |= set(known_posts or [])
        except AttributeError:
            self.known_posts = set(known_posts or [])

        self._collected_posts = []

        try:
            self._extract_all_posts()
        except (Exception, KeyboardInterrupt):
            self._collected_posts = []
            raise

        logger.info(f"Finished scanning. {len(self._collected_posts)} {'new ' if self.known_posts else ''}posts found.")

        collected_posts = self._collected_posts
        self._collected_posts = []

        self.known_posts |= set(collected_posts)
        return collected_posts

    def _extract_all_posts(self) -> None:
        raise NotImplementedError(f"{self} hasn't implemented posts extraction.")

    def _register_post(self,
                       post: PostUrl,
                       assets: Sequence[PostAssetUrl],
                       created_at: datetime | str | int,
                       score: int) -> None:
        if post in self.known_posts:
            raise EndScan(Exception)

        if post in self._collected_posts:
            raise NotImplementedError

        post.created_at = datetime_from_string(created_at)
        post.score = score

        post._assets = []  # what if revision?
        for asset in assets:
            post._register_asset(asset)

        self._collected_posts.append(post)
        logger.info(f"Found {len(self._collected_posts)} posts so far...")


class HasPostsOnJson(HasPosts):
    posts_json_url: str
    posts_objects_dig: list[str | int]

    def _extract_all_posts(self, /, posts_json_url: str | None = None) -> None:
        """Extract posts from a json endpoint."""
        if TYPE_CHECKING:
            assert isinstance(self, Feed | GalleryUrl)

        json_url = posts_json_url or self.posts_json_url

        page = 1
        logger.debug(f"Scanning {self} for posts...")
        while True:
            if self.quit_early_page and page > self.quit_early_page:
                logger.debug("Quitting early because it's a first-time scan...")
                return

            json_data = self.session.get_json_cached(json_url.format(page=page, self=self))
            post_objects = json_data
            logger.debug(f"At page {page}...")

            for dig_element in self.posts_objects_dig:
                try:
                    post_objects = post_objects[dig_element]
                except KeyError as e:
                    raise NotImplementedError(dig_element, post_objects.keys()) from e

            if not post_objects:
                if self.validate_existence_of_posts:
                    raise NotImplementedError("No posts found")
                logger.debug("No more posts found. Aborting...")
                return

            for post_dict_data in post_objects:
                try:
                    self._process_json_post(post_dict_data)
                except EndScan:
                    logger.debug("Reached a previously-seen post. Quitting...")
                    return
            logger.debug(f"{len(self._collected_posts)} posts collected so far.")
            page += 1

    def _process_json_post(self, post_object: dict) -> None:
        raise NotImplementedError(f"{self} hasn't implemented post object processing.")


class EndScan(Exception):  # noqa: N818
    pass
