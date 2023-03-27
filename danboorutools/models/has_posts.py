from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, final

from danboorutools import logger
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from datetime import datetime

    from danboorutools.models.url import PostAssetUrl, PostUrl

PostDataVar = TypeVar("PostDataVar")


class HasPosts(Generic[PostDataVar]):
    _collected_posts: list[PostUrl]
    known_posts: set[PostUrl]

    quit_early_page = 0

    @final
    def extract_posts(self, known_posts: list[PostUrl] | None = None) -> list[PostUrl]:
        try:
            self.known_posts |= set(known_posts or [])
        except AttributeError:
            self.known_posts = set(known_posts or [])

        self._collected_posts = []

        try:
            logger.info(f"Scanning {self} for posts...")
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
        for page, post_objects in enumerate(self._extract_posts_from_each_page()):
            logger.info(f"At page {page + 1}...")

            for post_data in post_objects:
                try:
                    self._process_post(post_data)
                except FoundKnownPost:
                    logger.info("Reached a previously-seen post. Quitting...")
                    return

            logger.info(f"{len(self._collected_posts)} posts collected so far.")

            if self.quit_early_page and page >= self.quit_early_page:
                logger.info("Quitting early because it's a first-time scan...")
                return

    def _extract_posts_from_each_page(self) -> Iterator[list[PostDataVar]]:
        raise NotImplementedError(f"{self} hasn't implemented page extraction.")

    def _process_post(self, post_object: PostDataVar) -> None:
        raise NotImplementedError(f"{self} hasn't implemented post object processing.")

    def _register_post(self,
                       post: PostUrl,
                       assets: Sequence[PostAssetUrl | str],
                       created_at: datetime | str | int,
                       score: int) -> None:
        if post in self.known_posts:
            raise FoundKnownPost(Exception)

        if post in self._collected_posts:
            raise NotImplementedError

        if not assets:
            # allowed to be empty so that revisions that become private, like fanbox or fantia,
            # still go through the known posts check in order to abort early during rescans
            return

        post.created_at = datetime_from_string(created_at)
        post.score = score

        post._assets = []  # what if revision?
        for asset in assets:
            post._register_asset(asset)

        self._collected_posts.append(post)
        logger.info(f"Found {len(self._collected_posts)} posts so far...")


class FoundKnownPost(Exception):  # noqa: N818
    pass
