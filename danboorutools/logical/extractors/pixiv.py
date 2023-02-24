from __future__ import annotations

from datetime import datetime

from danboorutools.exceptions import UrlIsDeleted
from danboorutools.logical.sessions.pixiv import PixivSession
from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, GalleryAssetUrl, InfoUrl, PostAssetUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.misc import memoize, settable_property
from danboorutools.util.time import datetime_from_string


class PixivUrl(Url):
    session = PixivSession()


class PixivProfileImageUrl(PostAssetUrl, PixivUrl):
    stacc: str | None = None


class PixivRequestUrl(ArtistAlbumUrl, PixivUrl):
    request_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        request_id = kwargs["request_id"]
        return f"https://www.pixiv.net/requests/{request_id}"


class PixivNovelSeriesUrl(ArtistAlbumUrl, PixivUrl):
    series_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        series_id = kwargs["series_id"]
        return f"https://www.pixiv.net/novel/series/{series_id}"


class PixivNovelUrl(PostUrl, PixivUrl):
    novel_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        novel_id = kwargs["series_id"]
        return f"https://www.pixiv.net/novel/show.php?id={novel_id}"


class PixivNovelImageUrl(PostAssetUrl, PixivUrl):
    novel_id: int | None
    stacc: str | None = None


class PixivGalleryAssetUrl(GalleryAssetUrl, PixivUrl):
    user_id: int


class PixivImageUrl(PostAssetUrl, PixivUrl):
    post_id: int
    page: int  # starts from 0

    unlisted: bool = False
    stacc: str | None

    def parse_filename(self, filename_stem: str, *date: str) -> None:
        if date:
            self.created_at = datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]),
                                       hour=int(date[3]), minute=int(date[4]), second=int(date[5]))

        match filename_stem.split("_"):
            case post_id, *rest:
                try:
                    self.post_id = int(post_id)
                except ValueError:
                    # https://i.pximg.net/img-original/img/2018/03/30/10/50/16/67982747-04d810bf32ebd071927362baec4057b6_p0.png
                    if "-" in post_id:
                        post_id, _private_string = post_id.split("-")
                        self.post_id = int(post_id)
                        self.unlisted = True
                for value in rest:
                    if value.startswith("p"):
                        self.page = int(value.removeprefix("p"))
                        return
                    elif value.startswith("ugoira"):
                        self.page = 0
                        return
                else:
                    self.page = 0
            case post_id, :
                self.post_id = int(post_id)
                self.page = 0

    @settable_property
    def post(self) -> PixivPostUrl:  # type: ignore[override]
        return self.build(PixivPostUrl, post_id=self.post_id, unlisted=self.unlisted)

    @property
    def full_size(self) -> str:
        if "img-original" in self.parsed_url.url_parts or "img-zip-ugoira" in self.parsed_url.url_parts:
            return self.parsed_url.raw_url
        else:
            raise NotImplementedError


class PixivPostUrl(PostUrl, PixivUrl):
    post_id: int | str  # int if not unlisted else str
    unlisted: bool = False

    @classmethod
    def normalize(cls, **kwargs) -> str:
        unlisted: bool = kwargs.get("unlisted", False)
        post_id: int | str = kwargs["post_id"]
        if unlisted:
            return f"https://www.pixiv.net/en/artworks/unlisted/{post_id}"
        else:
            return f"https://www.pixiv.net/en/artworks/{post_id}"

    @settable_property
    def assets(self) -> list[PixivImageUrl]:  # type: ignore[override]
        asset_urls = [img["urls"]["original"] for img in self._pages_data]
        if "_ugoira0" in asset_urls[0]:
            asset_urls = [self._ugoira_data["originalSrc"]]

        assets: list[PixivImageUrl] = [self.parse(url) for url in asset_urls]  # type: ignore[misc]
        assert all(isinstance(asset, PixivImageUrl) for asset in assets), assets

        return assets

    @settable_property
    def created_at(self) -> datetime:
        return datetime_from_string(self._post_data["createDate"])

    @settable_property
    def score(self) -> int:
        return int(self._post_data["likeCount"])

    @settable_property
    def gallery(self) -> PixivArtistUrl:  # type: ignore[override]
        return self.build(
            PixivArtistUrl,
            user_id=int(self._post_data["userId"])
        )

    @settable_property
    def is_deleted(self) -> bool:
        try:
            _ = self._post_data
            return False
        except UrlIsDeleted:
            return True

    @property
    def _post_data(self) -> dict:
        return self.session.get_json(f"https://www.pixiv.net/ajax/illust/{self.post_id}?lang=en")

    @property
    def _pages_data(self) -> dict:
        return self.session.get_json(f"https://www.pixiv.net/ajax/illust/{self.post_id}/pages?lang=en")

    @property
    def _ugoira_data(self) -> dict:
        return self.session.get_json(f"https://www.pixiv.net/ajax/illust/{self.post_id}/ugoira_meta?lang=en")


class PixivArtistUrl(ArtistUrl, PixivUrl):
    user_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        user_id = kwargs["user_id"]
        return f"https://www.pixiv.net/en/users/{user_id}"

    @settable_property
    def posts(self) -> list[PixivPostUrl]:  # type: ignore[override]
        page = 0
        posts: list[PixivPostUrl] = []
        while True:
            page += 1
            illusts = self._illust_data(page=page)
            if not illusts:
                return posts
            for illust_data in illusts:
                post = self.build(
                    PixivPostUrl,
                    post_id=int(illust_data["id"])
                )
                post.created_at = datetime_from_string(illust_data["upload_timestamp"])
                post.gallery = self
                post.score = int(illust_data.get("rating_count", 0))

                if int(illust_data["type"]) == 2:
                    post_ugoira_data = post._ugoira_data
                    asset_urls = [post_ugoira_data["originalSrc"]]
                else:
                    # Can't avoid fetching this for single-page posts because all samples are jpg, even for png files
                    post_pages_data = self.session.get_json(f"https://www.pixiv.net/ajax/illust/{post.post_id}/pages")
                    asset_urls = [img["urls"]["original"] for img in post_pages_data]
                post.assets = [self.parse(url) for url in asset_urls]  # type: ignore[misc]  # jesus christ shut the fuck up retard

                posts.append(post)

    @property
    def primary_names(self) -> list[str]:
        return [self._artist_data["user_name"]]

    @property
    def secondary_names(self) -> list[str]:
        return [
            self._artist_data["user_account"],
            f"pixiv {self.user_id}"
        ]

    @property
    def related(self) -> list[Url]:
        # pylint: disable=import-outside-toplevel
        from danboorutools.logical.extractors.fanbox import FanboxArtistUrl
        from danboorutools.logical.extractors.pixiv_sketch import PixivSketchArtistUrl

        urls: list[Url] = [
            self.build(PixivStaccUrl, stacc=self._artist_data["user_account"])
        ]

        if self._artist_data["fanbox_details"]:
            urls.append(
                self.build(FanboxArtistUrl, username=self._artist_data["fanbox_details"]["creator_id"])
            )

        sketch_url = self.build(PixivSketchArtistUrl, stacc=self._artist_data["user_account"])
        if not sketch_url.is_deleted:
            urls.append(sketch_url)

        if user_webpage := self._artist_data.get("user_webpage"):
            urls.append(self.parse(user_webpage))

        if social_data := self._artist_data["social"]:
            for url_dict in social_data.values():
                urls.append(self.parse(url_dict[Url]))

        return urls

    @settable_property
    def is_deleted(self) -> bool:
        try:
            _ = self._artist_data
            return False
        except UrlIsDeleted:
            return True

    @memoize
    def _illust_data(self, page: int = 1) -> dict:
        artist_data_url = f"https://www.pixiv.net/touch/ajax/user/illusts?id={self.user_id}&p={page}&lang=en"
        return self.session.get_json(artist_data_url)["illusts"]

    @property
    def _artist_data(self) -> dict:
        url = f"https://www.pixiv.net/touch/ajax/user/details?id={self.user_id}&lang=en"
        json = self.session.get_json(url)
        return json["user_details"]


class PixivMeUrl(RedirectUrl, PixivUrl):
    # Useful to have separate from Stacc, to get the pixiv ID indirectly

    stacc: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        stacc = kwargs["stacc"]
        return f"https://www.pixiv.net/stacc/{stacc}"


class PixivStaccUrl(InfoUrl, PixivUrl):
    stacc: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        stacc = kwargs["stacc"]
        return f"https://www.pixiv.net/stacc/{stacc}"

    @property
    def me_from_stacc(self) -> PixivMeUrl:
        return self.build(PixivMeUrl, stacc=self.stacc)

    @property
    def related(self) -> list[Url]:
        return [self.me_from_stacc.resolved]

    @settable_property
    def is_deleted(self) -> bool:
        return self.me_from_stacc.is_deleted

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.stacc]
