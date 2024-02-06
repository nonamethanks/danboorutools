from __future__ import annotations

import re
from functools import cached_property
from typing import TYPE_CHECKING

from danboorutools.logical.sessions.fanbox import FanboxArtistData, FanboxPostData, FanboxSession
from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, RedirectUrl, Url, parse_list

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import datetime

    from danboorutools.logical.feeds.fanbox import FanboxFeed


class FanboxUrl(Url):
    session = FanboxSession()


def _process_post(self: FanboxFeed | FanboxArtistUrl, post_object: int) -> None:
    post_data = self.session.post_data(post_object)

    post = FanboxPostUrl.build(
        username=post_data.creatorId,
        post_id=post_object,
    )

    self._register_post(
        post=post,
        assets=post_data.assets,
        created_at=post_data.publishedDatetime,
        score=post_data.likeCount,
    )


class FanboxArtistUrl(ArtistUrl, FanboxUrl):
    username: str  # it's not guaranteed that this is the stacc. it might change.

    normalize_template = "https://{username}.fanbox.cc"

    @property
    def artist_data(self) -> FanboxArtistData:
        return self.session.artist_data(self.username)

    @property
    def related(self) -> list[Url]:
        if self.is_deleted:
            return []
        return self.artist_data.related_urls

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []
        return [self.artist_data.user.name]

    @property
    def secondary_names(self) -> list[str]:
        if self.is_deleted:
            return [self.username]
        return list({self.artist_data.creatorId, self.username})

    def subscribe(self) -> None:
        return self.session.subscribe(self.username)

    def _extract_posts_from_each_page(self) -> Iterator[list[int]]:
        data_url = f"https://api.fanbox.cc/post.listCreator?creatorId={self.username}&limit=5"
        while True:
            page_json = self.session.get_and_parse_fanbox_json(data_url)

            if not (posts_json := page_json["items"]):
                return

            yield [post_json["id"] for post_json in posts_json if not int(post_json["feeRequired"])]
            if not (data_url := page_json["nextUrl"]):
                return

    _process_post = _process_post

    def _extract_assets(self) -> list[GalleryAssetUrl]:
        featured = self.artist_data.featured_images
        other_images = parse_list([self.artist_data.coverImageUrl, self.artist_data.user.iconUrl], GalleryAssetUrl)
        return featured + other_images


class FanboxPostUrl(PostUrl, FanboxUrl):
    username: str
    post_id: int

    normalize_template = "https://{username}.fanbox.cc/posts/{post_id}"

    @cached_property
    def gallery(self) -> FanboxArtistUrl:
        return FanboxArtistUrl.build(username=self.username)

    def _extract_assets(self) -> list[PostAssetUrl]:
        post_data = self.session.post_data(self.post_id)
        return post_data.assets

    @cached_property
    def created_at(self) -> datetime:
        return self.post_data.publishedDatetime

    @cached_property
    def score(self) -> int:
        return self.post_data.likeCount

    @property
    def post_data(self) -> FanboxPostData:
        return self.session.post_data(self.post_id)


class FanboxOldPostUrl(RedirectUrl, FanboxUrl):
    pixiv_id: int
    post_id: int

    normalize_template = "https://www.pixiv.net/fanbox/creator/{pixiv_id}/post/{post_id}"


class FanboxOldArtistUrl(RedirectUrl, FanboxUrl):

    # TODO: implement related pixiv -> fanbox and fanbox -> pixiv

    pixiv_id: int

    normalize_template = "https://www.pixiv.net/fanbox/creator/{pixiv_id}"


class FanboxArtistImageUrl(GalleryAssetUrl, FanboxUrl):
    pixiv_id: int
    image_type: str

    @property
    def full_size(self) -> str:
        return re.sub(r"\/[cw]\/\w+\/", "/", self.parsed_url.raw_url)


class FanboxAssetUrl(PostAssetUrl, FanboxUrl):
    # https://null.fanbox.cc/39714 TODO: use this to get the post -> dont assign directly, first fetch to check if alive
    post_id: int | None
    pixiv_id: int | None
    asset_type: str

    @property
    def full_size(self) -> str:
        return re.sub(r"\/[cw]\/\w+\/", "/", self.parsed_url.raw_url)
