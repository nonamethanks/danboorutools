from __future__ import annotations

import warnings
from datetime import UTC, datetime, timedelta
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
    _revised_posts: list[PostUrl | GalleryUrl]
    known_posts: list[PostUrl | GalleryUrl]

    quit_early_page = 0
    check_revisions = True
    max_post_age: timedelta | None = None

    first_page_must_have_posts = False

    last_id: str | int | None = None  # for feeds with high volume of data like twitter

    @final
    def extract_posts(self, known_posts: list[PostUrl | GalleryUrl] | None = None) -> None:
        try:
            self.known_posts += known_posts or []
        except AttributeError:
            self.known_posts = known_posts or []

        self._new_posts = []
        self._revised_posts = []

        try:
            logger.info(f"Scanning {self} for posts...")
            self.__extract_gallery_assets()
            self._extract_all_posts()
        except PostTooOldError as e:
            logger.info(f"Found a post that's too old for a first scan: {e.post}, {e.post.created_at}. Quitting...")
        except (Exception, KeyboardInterrupt):
            self._new_posts = []
            self._revised_posts = []
            raise

        self.print_progress(finished=True)

    def __extract_gallery_assets(self) -> None:
        from danboorutools.models.url import GalleryUrl
        if isinstance(self, GalleryUrl) and (gallery_assets := self._extract_assets()):
            for g_asset in gallery_assets:
                g_asset.gallery = self
            self._register_post(
                self,
                assets=gallery_assets,
                created_at=datetime.now(tz=UTC),
                score=0,
            )

    def _extract_all_posts(self) -> None:
        for page, post_objects in enumerate(self._extract_posts_from_each_page()):  # type: ignore[var-annotated]
            if not post_objects:
                if page == 0 and self.first_page_must_have_posts:
                    raise ValueError("No posts found on the first page.")
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

        from danboorutools.models.url import PostUrl

        if post in self._revised_posts or post in self._new_posts:
            raise NotImplementedError(post)

        if post in self.known_posts:
            post = self.known_posts[self.known_posts.index(post)]  # fuck

        post.is_deleted = is_deleted
        if isinstance(post, PostUrl):
            post.score = score
            post.created_at = datetime_from_string(created_at) if created_at else datetime.now(tz=UTC)

            # skip posts that are too old for a first scan (during feed scans etc)
            if self.max_post_age and post.created_at < datetime.now(tz=UTC) - self.max_post_age:
                raise PostTooOldError(post)

        self.__insert_post(post=post, found_assets=assets)

    def __insert_post(self, post: PostUrl | GalleryUrl, found_assets: Sequence[PostAssetUrl | GalleryAssetUrl | str]) -> None:
        old_assets: list[PostAssetUrl | GalleryAssetUrl] = list(post.__dict__.get("assets", []))  # new list
        has_new_assets = False
        for asset in found_assets:
            try:
                post._register_asset(asset, is_deleted=False)
            except DuplicateAssetError:
                pass
            else:
                has_new_assets = True

        # check for removed versions
        found_asset_urls = [u if not isinstance(u, str) else post.parse(u) for u in found_assets]
        deletion_status_changed = False
        for asset in old_assets:
            if asset not in found_asset_urls:
                # this asset was removed from the source
                if not asset.__dict__.get("is_deleted", False):
                    logger.debug(f"Detected that asset {asset} for post {post} was deleted at the source.")
                    asset.is_deleted = True
                    deletion_status_changed = True
            else:  # noqa: PLR5501
                if asset.__dict__.get("is_deleted", False):
                    # this asset was restored at the source
                    logger.debug(f"Detected that asset {asset} for post {post} was restored at the source.")
                    asset.is_deleted = False
                    deletion_status_changed = True

        # check if it's a revision, a new post, or nothing at all
        if has_new_assets and old_assets:
            # has both old and new assets
            logger.debug(f"Found new assets on a previously seen post: {post}.")
            warnings.warn("Found a previously seen post.", FoundKnownPost, stacklevel=2)
            self._revised_posts.append(post)
        elif deletion_status_changed:
            logger.debug(f"Some assets on post {post} changed deletion status.")
            warnings.warn("Found a previously seen post.", FoundKnownPost, stacklevel=2)
            self._revised_posts.append(post)
        elif has_new_assets and not old_assets:
            # only has new assets
            logger.debug(f"Found a new post: {post}.")
            self._new_posts.append(post)
        elif not has_new_assets and old_assets:
            # only has old assets
            logger.debug(f"Found a previously seen post: {post}.")
            warnings.warn("Found a previously seen post.", FoundKnownPost, stacklevel=2)
            return
        elif not has_new_assets and not old_assets:
            # no post
            return

        self.print_progress()

    def print_progress(self, finished: bool = False) -> None:
        message = ""

        if finished:
            message += "Finished scanning. "

        message += "Found "

        if not self._new_posts and not self._revised_posts:
            message += "no posts" if not self.known_posts else "no new posts"
        else:
            if self._new_posts:
                message += f"{len(self._new_posts)} new posts"

                if self._revised_posts:
                    message += " and "

            if self._revised_posts:
                message += f"{len(self._revised_posts)} revised posts"

        if not finished:
            message += " so far"

        message += "."

        logger.info(message)


class FoundKnownPost(Warning):
    pass


class PostTooOldError(Exception):
    def __init__(self, post: PostUrl) -> None:
        self.post = post
        super().__init__()
