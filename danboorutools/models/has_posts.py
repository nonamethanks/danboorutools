from __future__ import annotations

import warnings
from datetime import UTC, datetime
from typing import TYPE_CHECKING, TypeVar, final, overload

from danboorutools import logger
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from danboorutools.models.url import GalleryAssetUrl, GalleryUrl, PostAssetUrl, PostUrl

    PostT = TypeVar("PostT")


class HasPosts:
    _collected_posts: list[PostUrl | GalleryUrl]
    known_posts: list[PostUrl | GalleryUrl]

    quit_early_page = 0
    check_revisions = True
    max_post_age: datetime | None = None

    @final
    def extract_posts(self, known_posts: list[PostUrl | GalleryUrl] | None = None) -> list[PostUrl | GalleryUrl]:
        try:
            self.known_posts += known_posts or []
        except AttributeError:
            self.known_posts = known_posts or []

        self._collected_posts = []

        try:
            logger.info(f"Scanning {self} for posts...")
            self._extract_all_posts()
        except PostTooOldError:
            logger.info("Found a post that's too old during a first-time scan. Quitting...")
        except (Exception, KeyboardInterrupt):
            self._collected_posts = []
            raise

        diff = len([p for p in self._collected_posts if p not in self.known_posts])
        logger.info(f"Finished scanning. {diff} {"new " if self.known_posts else ""}posts found.")

        collected_posts = self._collected_posts
        self._collected_posts = []

        self.known_posts += set(collected_posts)
        return collected_posts

    def _extract_all_posts(self) -> None:
        from danboorutools.models.url import GalleryUrl
        if isinstance(self, GalleryUrl) and (g_assets := self._extract_assets()):
            self._register_post(
                self,
                assets=g_assets,
                created_at=datetime.now(tz=UTC),
                score=0,
            )

        for page, post_objects in enumerate(self._extract_posts_from_each_page()):  # type: ignore[var-annotated]
            if not post_objects:
                logger.info("No more posts found. Quitting...")
                return

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

            if not self.known_posts and self.quit_early_page > 0 and page + 1 >= self.quit_early_page:
                logger.info("Quitting early because it's a first-time scan...")
                return

            if seen_previous_post:
                logger.info("Quitting early because a previously-seen post was encountered...")
                return

    def _extract_posts_from_each_page(self) -> Iterator[list[PostT]]:
        raise NotImplementedError(f"{self} hasn't implemented page extraction.")

    def _process_post(self, post_object: PostT) -> None:
        raise NotImplementedError(f"{self} hasn't implemented post object processing.")

    @overload
    def _register_post(self, post: GalleryUrl, assets: Sequence[GalleryAssetUrl | str], created_at: datetime | str | int | None, score: int, is_deleted: bool = False) -> None:  # noqa: E501
        ...

    @overload
    def _register_post(self, post: PostUrl, assets: Sequence[PostAssetUrl | str], created_at: datetime | str | int | None, score: int, is_deleted: bool = False) -> None:  # noqa: E501
        ...

    def _register_post(self,  # noqa: PLR0913
                       post: PostUrl | GalleryUrl,
                       assets: Sequence[PostAssetUrl | GalleryAssetUrl | str],
                       created_at: datetime | str | int | None,
                       score: int,
                       is_deleted: bool = False,
                       ) -> None:
        if post in self.known_posts:
            logger.info(f"Found a previously-seen post: {post}. Rescanning.")
            warnings.warn("Found a previously seen post.", FoundKnownPost, stacklevel=2)
            # No need to reassign, because urls are cached

        if post in self._collected_posts:
            raise NotImplementedError(post)

        if not assets and not post.__dict__.get("assets"):
            return

        post.created_at = datetime_from_string(created_at) if created_at else datetime.now(tz=UTC)

        if not self.known_posts and (self.max_post_age and post.created_at < datetime.now(tz=UTC) - self.max_post_age):
            raise PostTooOldError

        post.score = score
        post.is_deleted = is_deleted

        for asset in assets:
            post._register_asset(asset)

        self._collected_posts.append(post)
        logger.info(f"Found {len(self._collected_posts):>4} posts so far. Last collected: {post}")


class FoundKnownPost(Warning):
    pass


class PostTooOldError(Exception):
    pass
