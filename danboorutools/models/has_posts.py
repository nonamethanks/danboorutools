from __future__ import annotations

import warnings
from datetime import UTC, datetime
from typing import TYPE_CHECKING, TypeVar, final, overload

from danboorutools import logger
from danboorutools.exceptions import DuplicateAssetError
from danboorutools.util.time import datetime_from_string

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from danboorutools.models.url import GalleryAssetUrl, GalleryUrl, PostAssetUrl, PostUrl

    PostT = TypeVar("PostT")


class HasPosts:
    _new_posts: list[PostUrl | GalleryUrl]
    _revisioned_posts: list[PostUrl | GalleryUrl]
    known_posts: list[PostUrl | GalleryUrl]

    quit_early_page = 0
    check_revisions = True
    max_post_age: datetime | None = None

    @final
    def extract_posts(self, known_posts: list[PostUrl | GalleryUrl] | None = None) -> None:
        try:
            self.known_posts += known_posts or []
        except AttributeError:
            self.known_posts = known_posts or []

        self._new_posts = []
        self._revisioned_posts = []

        try:
            logger.info(f"Scanning {self} for posts...")
            self._extract_all_posts()
        except PostTooOldError:
            logger.info("Found a post that's too old during a first-time scan. Quitting...")
        except (Exception, KeyboardInterrupt):
            self._new_posts = []
            self._revisioned_posts = []
            raise

        logger.info(
            "Finished scanning. ",
            f" {self._new_posts} {"new " if self.known_posts else ""}posts found.",
            f" {self._revisioned_posts} posts with revisions found." if self._revisioned_posts else "",
        )

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

        if post in self._revisioned_posts or post in self._new_posts:
            raise NotImplementedError(post)

        post.score = score
        post.is_deleted = is_deleted
        post.created_at = datetime_from_string(created_at) if created_at else datetime.now(tz=UTC)

        # skip posts that are too old for a first scan (during feed scans etc)
        if not self.known_posts and (self.max_post_age and post.created_at < datetime.now(tz=UTC) - self.max_post_age):
            raise PostTooOldError

        self.__insert_post(post=post, found_assets=assets)

    def __insert_post(self, post: PostUrl | GalleryUrl, found_assets: Sequence[PostAssetUrl | GalleryAssetUrl | str]) -> None:
        old_assets: list[PostAssetUrl | GalleryAssetUrl] = list(post.__dict__.get("assets", []))  # new list
        has_new_assets = False
        for asset in found_assets:
            try:
                post._register_asset(asset)
            except DuplicateAssetError:
                pass
            else:
                has_new_assets = True

        # check if it's a revision, a new post, or nothing at all
        if has_new_assets and old_assets:
            # has both old and new assets
            self._revisioned_posts.append(post)
        elif has_new_assets and not old_assets:
            # only has new assets
            self._new_posts.append(post)
        elif not has_new_assets and old_assets:
            # only has old assets
            return
        elif not has_new_assets and not old_assets:
            # no post
            return

        # check for removed versions
        found_asset_urls = [u if not isinstance(u, str) else post.parse(u) for u in found_assets]
        for asset in old_assets:
            if asset not in found_asset_urls:
                # this asset was removed from the source
                logger.info(f"Detected that asset {asset} for post {post} was deleted at the source.")
                asset.is_deleted = True
            else:
                # still there
                asset.is_deleted = False

        self.print_progress(post)

    def print_progress(self, post: PostUrl | GalleryUrl) -> None:
        logger.info(
            f"Found {len(self._new_posts):>3} posts ",
            f"and {len(self._revisioned_posts)} revisions" if self.known_posts else "",
            f" so far. Last collected: {post}",
        )


class FoundKnownPost(Warning):
    pass


class PostTooOldError(Exception):
    pass
