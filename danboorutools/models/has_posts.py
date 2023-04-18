from __future__ import annotations

import warnings
from datetime import datetime
from typing import TYPE_CHECKING, Any, final

from pytz import UTC

from danboorutools import logger
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from danboorutools.models.url import PostAssetUrl, PostUrl


class HasPosts:
    _collected_posts: list[PostUrl]
    known_posts: list[PostUrl]

    quit_early_page = 0
    check_revisions = True

    @final
    def extract_posts(self, known_posts: list[PostUrl] | None = None) -> list[PostUrl]:
        try:
            self.known_posts += known_posts or []
        except AttributeError:
            self.known_posts = known_posts or []

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

        self.known_posts += set(collected_posts)
        return collected_posts

    def _extract_all_posts(self) -> None:
        for page, post_objects in enumerate(self._extract_posts_from_each_page()):
            logger.info(f"At page {page + 1}...")

            seen_previous_post = False
            for post_data in post_objects:
                with warnings.catch_warnings(record=True, category=FoundKnownPost) as warning:
                    self._process_post(post_data)
                    if warning:
                        if not self.check_revisions:
                            logger.info("Found a previously-seen post. Quitting...")
                            return

                        seen_previous_post = True

            if self.quit_early_page and page + 1 >= self.quit_early_page:
                logger.info("Quitting early because it's a first-time scan...")
                return

            if seen_previous_post:
                logger.info("Quitting early because a previously-seen post was encountered...")
                return

    def _extract_posts_from_each_page(self) -> Iterator[list]:
        raise NotImplementedError(f"{self} hasn't implemented page extraction.")

    def _process_post(self, post_object: Any) -> None:  # noqa: ANN401
        raise NotImplementedError(f"{self} hasn't implemented post object processing.")

    def _register_post(self,  # noqa: PLR0913
                       post: PostUrl,
                       assets: Sequence[PostAssetUrl | str],
                       created_at: datetime | str | int | None,
                       score: int,
                       is_deleted: bool = False,
                       ) -> None:
        if post in self.known_posts:
            warnings.warn("Found a previously seen post.", FoundKnownPost)
            # No need to reassign, because urls are cached

        if post in self._collected_posts:
            raise NotImplementedError(post)

        if not assets:
            # allowed to be empty so that revisions that become private, like fanbox or fantia,
            # still go through the known posts check in order to abort early during rescans
            return

        post.created_at = datetime_from_string(created_at) if created_at else datetime.now(tz=UTC)
        post.score = score
        post.is_deleted = is_deleted

        for asset in assets:
            post._register_asset(asset)

        self._collected_posts.append(post)
        logger.info(f"Found {len(self._collected_posts):>4} posts so far. Last collected: {post}")


class FoundKnownPost(Warning):
    pass
