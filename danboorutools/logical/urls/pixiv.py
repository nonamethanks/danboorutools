from __future__ import annotations

import re
from functools import cached_property
from itertools import count, repeat, starmap
from typing import TYPE_CHECKING

from requests.exceptions import ProxyError

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions.pixiv import PixivArtistData, PixivGroupedIllustData, PixivSession, PixivSingleIllustData
from danboorutools.models.url import (
    ArtistAlbumUrl,
    ArtistUrl,
    GalleryAssetUrl,
    InfoUrl,
    PostAssetUrl,
    PostUrl,
    RedirectUrl,
    Url,
    parse_list,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from datetime import datetime

    from danboorutools.logical.feeds.pixiv import PixivFeed
    from danboorutools.models.file import File


class PixivUrl(Url):
    session = PixivSession()


class PixivProfileImageUrl(GalleryAssetUrl, PixivUrl):
    stacc: str | None = None

    @property
    def full_size(self) -> str:
        return re.sub(r"_\d+\.(\w+)$", r".\1", self.parsed_url.raw_url)


class PixivGalleryAssetUrl(GalleryAssetUrl, PixivUrl):
    user_id: int

    @property
    def full_size(self) -> str:
        return re.sub(r"\/[cw]\/\w+\/", "/", self.parsed_url.raw_url)


class PixivRequestUrl(ArtistAlbumUrl, PixivUrl):
    request_id: int

    normalize_template = "https://www.pixiv.net/requests/{request_id}"


class PixivNovelSeriesUrl(ArtistAlbumUrl, PixivUrl):
    series_id: int

    normalize_template = "https://www.pixiv.net/novel/series/{series_id}"


class PixivNovelUrl(PostUrl, PixivUrl):
    novel_id: int

    normalize_template = "https://www.pixiv.net/novel/show.php?id={novel_id}"


class PixivNovelImageUrl(PostAssetUrl, PixivUrl):
    novel_id: int | None
    stacc: str | None = None

    @property
    # https://i.pximg.net/novel-cover-original/img/2018/08/18/19/45/23/10008846_215387d3665210eed0a7cc564e4c93f3.png
    # https://i.pximg.net/c/600x600/novel-cover-master/img/2018/08/18/19/45/23/10008846_215387d3665210eed0a7cc564e4c93f3_master1200.jpg
    def full_size(self) -> str:
        if "novel-cover-original" in self.parsed_url.url_parts or "novel" in self.parsed_url.url_parts:
            return self.parsed_url.raw_url
        raise NotImplementedError


class PixivImageUrl(PostAssetUrl, PixivUrl):
    post_id: int
    page: int  # starts from 0

    stacc: str | None = None
    unlisted: bool = False

    page_regex = re.compile(r"^p(\d+)$")

    def extract_files(self) -> list[File]:
        downloaded_file = self.session.download_file(self.normalized_url)
        return [downloaded_file]  # don't try to extract ugoiras

    @classmethod
    def parse_filename(cls, filename_stem: str) -> tuple[int, int, bool]:
        parts = filename_stem.split("_")
        unlisted = False
        page = 0
        post_id_str, *parts = parts
        try:
            post_id = int(post_id_str)
        except ValueError:
            unlisted = True
            post_id_str, _private_hash = post_id_str.split("-")
            post_id = int(post_id_str)
        for part in parts:
            if match := cls.page_regex.match(part):
                page = int(match.groups()[0])
                break

        return post_id, page, unlisted

    @cached_property
    def post(self) -> PixivPostUrl:
        return PixivPostUrl.build(post_id=self.post_id, unlisted=self.unlisted)

    @property
    def full_size(self) -> str:
        if "img-original" in self.parsed_url.url_parts or "img-zip-ugoira" in self.parsed_url.url_parts:
            return self.parsed_url.raw_url
        else:
            raise NotImplementedError(self)

    @cached_property
    def gallery(self) -> PixivArtistUrl | PixivStaccUrl | None:
        if not self.stacc:
            return None

        stacc = PixivStaccUrl.build(stacc=self.stacc)
        try:
            return stacc.me_from_stacc.resolved
        except DeadUrlError:
            return stacc
        except ProxyError as e:
            if "Remote end closed connection without response" in str(e):
                return stacc
            raise


class PixivPostUrl(PostUrl, PixivUrl):
    post_id: int | str  # int if not unlisted else str
    unlisted: bool = False

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_id: int | str = kwargs["post_id"]
        if kwargs.get("unlisted", False):
            if isinstance(post_id, int):
                raise NotImplementedError("Wrong normalization, I need to figure this out")
            return f"https://www.pixiv.net/en/artworks/unlisted/{post_id}"
        else:
            return f"https://www.pixiv.net/en/artworks/{post_id}"

    def _extract_assets(self) -> list[PixivImageUrl]:
        asset_urls = [img["urls"]["original"] for img in self._pages_data]
        if "_ugoira0" in asset_urls[0]:
            asset_urls = [self.ugoira_data["originalSrc"]]

        return parse_list(asset_urls, PixivImageUrl)

    @cached_property
    def created_at(self) -> datetime:
        return self.post_data.createDate

    @cached_property
    def score(self) -> int:
        return self.post_data.likeCount

    @cached_property
    def gallery(self) -> PixivArtistUrl:
        return PixivArtistUrl.build(user_id=self.post_data.userId)

    @cached_property
    def is_deleted(self) -> bool:
        try:
            _ = self.post_data
        except DeadUrlError:
            return True
        else:
            return False

    @property
    def post_data(self) -> PixivSingleIllustData:
        post_id = f"unlisted/{self.post_id}" if self.unlisted else self.post_id
        return self.session.post_data(post_id)  # but does this work for unlisted?

    @property
    def _pages_data(self) -> dict:
        post_id = f"unlisted/{self.post_id}" if self.unlisted else self.post_id
        return self.session.get_api(f"https://www.pixiv.net/ajax/illust/{post_id}/pages?lang=en")

    @property
    def ugoira_data(self) -> dict:
        post_id = f"unlisted/{self.post_id}" if self.unlisted else self.post_id
        return self.session.get_api(f"https://www.pixiv.net/ajax/illust/{post_id}/ugoira_meta?lang=en")


def _process_post(self: PixivArtistUrl | PixivFeed, post_object: PixivGroupedIllustData) -> None:
    # kept separate so it can be imported by PixivFeed
    post = PixivPostUrl.build(post_id=post_object.id)
    post.gallery = PixivArtistUrl.build(user_id=post_object.user_id)

    if post_object.type == 2:
        post_ugoira_data = post.ugoira_data
        asset_urls = [post_ugoira_data["originalSrc"]]
    else:
        # Can't avoid fetching this for single-page posts because all samples are jpg, even for png files
        post_pages_data = self.session.get_api(f"https://www.pixiv.net/ajax/illust/{post.post_id}/pages")
        asset_urls = [img["urls"]["original"] for img in post_pages_data]

    if isinstance(self, PixivArtistUrl):
        score = post_object.rating_count  # the feed doesn't have this
        assert score is not None
    else:
        score = 0

    self._register_post(
        post=post,
        assets=[Url.parse(url) for url in asset_urls],
        created_at=post_object.upload_timestamp,
        score=score,
    )


class PixivArtistUrl(ArtistUrl, PixivUrl):
    user_id: int

    normalize_template = "https://www.pixiv.net/en/users/{user_id}"

    def _extract_posts_from_each_page(self) -> Iterator[list[PixivGroupedIllustData]]:
        return starmap(self.session.get_user_illusts, zip(repeat(self.user_id), count(1), strict=True))

    _process_post = _process_post

    @property
    def primary_names(self) -> list[str]:
        if not self.is_deleted:
            return [self.artist_data.user_name]
        else:
            return []

    @property
    def secondary_names(self) -> list[str]:
        if not self.is_deleted:
            return [self.artist_data.user_account, f"pixiv {self.user_id}"]
        else:
            return [f"pixiv {self.user_id}"]

    @property
    def related(self) -> list[Url]:
        return [*self.artist_data.related_urls, self.stacc_url]

    @property
    def stacc_url(self) -> PixivStaccUrl:
        return PixivStaccUrl.build(stacc=self.artist_data.user_account)

    @property
    def artist_data(self) -> PixivArtistData:
        return self.session.artist_data(self.user_id)

    def _extract_assets(self) -> list[GalleryAssetUrl]:
        imgs = [self.artist_data.profile_image_full]
        if self.artist_data.cover_image_full:
            imgs += [self.artist_data.cover_image_full]
        return imgs

    def subscribe(self) -> None:
        self.session.subscribe(self.user_id)


class PixivMeUrl(RedirectUrl, PixivUrl):
    # Useful to have separate from Stacc, to get the pixiv ID indirectly
    stacc: str

    normalize_template = "https://pixiv.me/{stacc}"


class PixivStaccUrl(InfoUrl, PixivUrl):
    stacc: str

    normalize_template = "https://www.pixiv.net/stacc/{stacc}"

    @property
    def me_from_stacc(self) -> PixivMeUrl:
        return PixivMeUrl.build(stacc=self.stacc)

    @property
    def related(self) -> list[Url]:
        return [self.me_from_stacc.resolved]

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.stacc]
