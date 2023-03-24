from __future__ import annotations

from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING

from pytz import UTC
from requests.exceptions import ProxyError

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions.pixiv import PixivArtistData, PixivArtistIllustData, PixivPostData, PixivSession
from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, GalleryAssetUrl, InfoUrl, PostAssetUrl, PostUrl, RedirectUrl, Url

if TYPE_CHECKING:
    from danboorutools.logical.feeds.pixiv import PixivFeed


class PixivUrl(Url):
    session = PixivSession()


class PixivProfileImageUrl(PostAssetUrl, PixivUrl):
    stacc: str | None = None

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url


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


class PixivGalleryAssetUrl(GalleryAssetUrl, PixivUrl):
    user_id: int

    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url


class PixivImageUrl(PostAssetUrl, PixivUrl):
    post_id: int
    page: int  # starts from 0

    unlisted: bool = False
    stacc: str | None

    def parse_filename(self, filename_stem: str, *date: str) -> None:
        if date:
            self.created_at = datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]),
                                       hour=int(date[3]), minute=int(date[4]), second=int(date[5]), tzinfo=UTC)

        match filename_stem.split("_"):
            case post_id, *rest:
                try:
                    self.post_id = int(post_id)
                except ValueError:
                    # https://i.pximg.net/img-original/img/2018/03/30/10/50/16/67982747-04d810bf32ebd071927362baec4057b6_p0.png
                    if "-" in post_id:
                        post_id, _private_string = post_id.split("-")
                        self.post_id = int(post_id)  # this is wrong: the post cannot be accessed this way
                        self.unlisted = True
                for value in rest:
                    if value.startswith("p"):
                        self.page = int(value.removeprefix("p"))
                        return
                    elif value.startswith("ugoira"):
                        self.page = 0
                        return
                self.page = 0
            case post_id, :
                self.post_id = int(post_id)
                self.page = 0

    @cached_property
    def post(self) -> PixivPostUrl:
        return self.build(PixivPostUrl, post_id=self.post_id, unlisted=self.unlisted)

    @property
    def full_size(self) -> str:
        if "img-original" in self.parsed_url.url_parts or "img-zip-ugoira" in self.parsed_url.url_parts:
            return self.parsed_url.raw_url
        else:
            raise NotImplementedError(self)

    @property
    def gallery(self) -> PixivArtistUrl | PixivStaccUrl | None:
        if not self.stacc:
            return None

        try:
            return self.build(PixivStaccUrl, stacc=self.stacc).me_from_stacc.resolved
        except DeadUrlError:
            return self.build(PixivStaccUrl, stacc=self.stacc)
        except ProxyError as e:
            if "Remote end closed connection without response" in str(e):
                return self.build(PixivStaccUrl, stacc=self.stacc)
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

    def _extract_assets(self) -> None:
        asset_urls = [img["urls"]["original"] for img in self._pages_data]
        if "_ugoira0" in asset_urls[0]:
            asset_urls = [self.ugoira_data["originalSrc"]]

        for asset_url in asset_urls:
            self._register_asset(asset_url)

    @cached_property
    def created_at(self) -> datetime:
        return self._post_data.createDate

    @cached_property
    def score(self) -> int:
        return self._post_data.likeCount

    @cached_property
    def gallery(self) -> PixivArtistUrl:
        return self.build(PixivArtistUrl, user_id=self._post_data.userId)

    @cached_property
    def is_deleted(self) -> bool:
        try:
            _ = self._post_data
        except DeadUrlError:
            return True
        else:
            return False

    @property
    def _post_data(self) -> PixivPostData:
        post_id = f"unlisted/{self.post_id}" if self.unlisted else self.post_id
        return self.session.post_data(post_id)  # but does this work for unlisted?

    @property
    def _pages_data(self) -> dict:
        post_id = f"unlisted/{self.post_id}" if self.unlisted else self.post_id
        return self.session.get_json(f"https://www.pixiv.net/ajax/illust/{post_id}/pages?lang=en")

    @property
    def ugoira_data(self) -> dict:
        post_id = f"unlisted/{self.post_id}" if self.unlisted else self.post_id
        return self.session.get_json(f"https://www.pixiv.net/ajax/illust/{post_id}/ugoira_meta?lang=en")


def _process_post_from_json(self: PixivArtistUrl | PixivFeed, post_object: dict) -> None:  # kept separate so it can be imported by PixivFeed
    post_data = PixivArtistIllustData(**post_object)
    post = PixivPostUrl.build(PixivPostUrl, post_id=post_data.id)

    if post_data.type == 2:
        post_ugoira_data = post.ugoira_data
        asset_urls = [post_ugoira_data["originalSrc"]]
    else:
        # Can't avoid fetching this for single-page posts because all samples are jpg, even for png files
        post_pages_data = self.session.get_json(f"https://www.pixiv.net/ajax/illust/{post.post_id}/pages")
        asset_urls = [img["urls"]["original"] for img in post_pages_data]

    if isinstance(self, PixivArtistUrl):
        score = post_data.rating_count  # the feed doesn't have this
        assert score is not None
    else:
        score = 0

    self._register_post(
        post=post,
        assets=[Url.parse(url) for url in asset_urls],  # type: ignore[misc]
        created_at=post_data.upload_timestamp,
        score=score,
    )


class PixivArtistUrl(ArtistUrl, PixivUrl):
    user_id: int

    normalize_template = "https://www.pixiv.net/en/users/{user_id}"

    posts_json_url = "https://www.pixiv.net/touch/ajax/user/illusts?id={self.user_id}&p={page}&lang=en"
    posts_objects_dig = ["body", "illusts"]

    _process_post_from_json = _process_post_from_json

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
        return self.build(PixivStaccUrl, stacc=self.artist_data.user_account)

    @property
    def artist_data(self) -> PixivArtistData:
        return self.session.artist_data(self.user_id)


class PixivMeUrl(RedirectUrl, PixivUrl):
    # Useful to have separate from Stacc, to get the pixiv ID indirectly
    stacc: str

    normalize_template = "https://pixiv.me/{stacc}"

    resolved: PixivArtistUrl


class PixivStaccUrl(InfoUrl, PixivUrl):
    stacc: str

    normalize_template = "https://www.pixiv.net/stacc/{stacc}"

    @property
    def me_from_stacc(self) -> PixivMeUrl:
        return self.build(PixivMeUrl, stacc=self.stacc)

    @property
    def related(self) -> list[Url]:
        return [self.me_from_stacc.resolved]

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.stacc]
