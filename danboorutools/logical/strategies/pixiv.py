from datetime import datetime
from functools import cached_property

from danboorutools.logical.sessions.pixiv import PixivSession
from danboorutools.models.url import ArtistUrl, AssetUrl, InfoUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.misc import compile_url, memoize, settable_property
from danboorutools.util.time import datetime_from_string

BASE_DOMAIN = compile_url(r"https?:\/\/(?:(?:www|touch)\.)?pixiv\.net")
POST_PATTERN = compile_url(BASE_DOMAIN, r"\/(?:member(?:_illust)?.php\?.*illust_id=(?P<post_id>\d+)|(?:en\/)?artworks\/(?P<post_id>\d+))")
ARTIST_PATTERN = compile_url(BASE_DOMAIN,
                             r"\/(?:(?:member(?:_illust)?|mypage)\.php[?#]id=|(?:en\/)?(?:u(?:sers)?\/|#id=))(?P<artist_id>\d+)")
IMAGE_PATTERN = compile_url(
    r"https?:\/\/(?:i|img)(?:\d*|[\w-]*)\.(?:pximg|pixiv)\.net\/"
    r"(?:(?:\w)*\/)*img(?:-original|[\w-]*)?\/(?:img\/)?(?:\w*\/)*"
    r"(?:(?:(?P<post_id>\d{3,})(?:_(?:m|(?:big_)?(?:(?:p|ugoira)(?:\d+)+(?:_master\d+)?)))?)"
    r"|(?:[\w-]+\/(?P<post_id>\d+)(?:_p\d+)?))(?:_big_p\d+|_ugoira\d+x\d+|_m)?\.(?:png|jpg|gif|jpeg|zip)(?:\?\d+)?"
)

ME_PATTERN = compile_url(r"https?:\/\/(?:www\.)?pixiv\.me\/(?P<me_id>[^\/]+)")
STACC_PATTERN = compile_url(r"https?:\/\/(?:www\.)?pixiv\.net\/stacc\/(?P<stacc_id>[^/]+)/?")


class PixivUrl(Url):  # pylint: disable=abstract-method
    session = PixivSession()


class PixivImageUrl(AssetUrl, PixivUrl):
    domains = ["pximg.net"]
    id_name = "post_id"
    patterns = {IMAGE_PATTERN: None}

    @settable_property
    def created_at(self) -> datetime:
        # https://i.pximg.net/img-original/img/2022/12/01/02/55/19/103238684_p0.jpg
        url_parts = list(map(int, self.normalized_url.split("/")[5:11]))
        return datetime(
            year=url_parts[0],
            month=url_parts[1],
            day=url_parts[2],
            hour=url_parts[3],
            minute=url_parts[4],
            second=url_parts[5],
        )

    @settable_property
    def post(self) -> "PixivPostUrl":  # type: ignore[override]
        return self.build(PixivPostUrl, post_id=self.id)


class PixivPostUrl(PostUrl, PixivUrl):
    domains = ["pixiv.net"]
    id_name = "post_id"
    patterns = {POST_PATTERN: "https://www.pixiv.net/en/artworks/{post_id}"}

    @settable_property
    def assets(self) -> list[PixivImageUrl]:  # type: ignore[override]
        json_pages_data = self.session.get_json(f"https://www.pixiv.net/ajax/illust/{self.id}/pages")

        asset_urls = [img["urls"]["original"] for img in json_pages_data]
        if "_ugoira0" in asset_urls[0]:
            asset_urls = [self.ugoira_data["originalSrc"]]
        assets: list[PixivImageUrl] = [self.parse(url) for url in asset_urls]  # type: ignore[misc]

        return assets

    @settable_property
    def created_at(self) -> datetime:
        return datetime_from_string(self.post_data["createDate"])

    @settable_property
    def score(self) -> int:
        return int(self.post_data["likeCount"])

    @settable_property
    def gallery(self) -> "PixivArtistUrl":  # type: ignore[override]
        return self.build(
            PixivArtistUrl,
            artist_id=self.post_data["userId"]
        )

    @cached_property
    def post_data(self) -> dict:
        return self.session.get_json(f"https://www.pixiv.net/ajax/illust/{self.id}")

    @cached_property
    def pages_data(self) -> dict:
        return self.session.get_json(f"https://www.pixiv.net/ajax/illust/{self.id}/pages")

    @cached_property
    def ugoira_data(self) -> dict:
        return self.session.get_json(f"https://www.pixiv.net/ajax/illust/{self.id}/ugoira_meta?lang=en")


class PixivArtistUrl(ArtistUrl, PixivUrl):
    domains = ["pixiv.net"]
    id_name = "artist_id"
    patterns = {ARTIST_PATTERN: "https://www.pixiv.net/en/users/{artist_id}"}

    @settable_property
    def posts(self) -> list[PixivPostUrl]:  # type: ignore[override]
        page = 0
        posts: list[PixivPostUrl] = []
        while True:
            page += 1
            illusts = self.illust_data(page=page)
            if not illusts:
                return posts
            for illust_data in illusts:
                post = self.build(
                    PixivPostUrl,
                    post_id=illust_data["id"]
                )
                post.created_at = datetime_from_string(illust_data["upload_timestamp"])
                post.gallery = self
                post.score = int(illust_data.get("rating_count", 0))

                if int(illust_data["type"]) == 2:
                    post_ugoira_data = post.ugoira_data
                    asset_urls = [post_ugoira_data["originalSrc"]]
                else:
                    # Can't avoid fetching this for single-page posts because all samples are jpg, even for png files
                    post_pages_data = self.session.get_json(f"https://www.pixiv.net/ajax/illust/{post.id}/pages")
                    asset_urls = [img["urls"]["original"] for img in post_pages_data]
                post.assets = [self.parse(url) for url in asset_urls]  # type: ignore[misc]  # jesus christ shut the fuck up retard

                posts.append(post)

    @memoize
    def illust_data(self, page: int = 1) -> dict:
        artist_data_url = f"https://www.pixiv.net/touch/ajax/user/illusts?id={self.id}&p={page}&lang=en"
        return self.session.get_json(artist_data_url)["illusts"]

    @cached_property
    def artist_data(self) -> dict:
        url = f"https://www.pixiv.net/touch/ajax/user/details?id={self.id}&lang=en"
        json = self.session.get_json(url)
        return json["user_details"]

    @property
    def names(self) -> list[str]:
        return [
            self.artist_data["user_name"],
            self.artist_data["user_account"],
            f"pixiv #{self.id}"
        ]

    @property
    def related(self) -> list[Url]:
        urls: list[Url] = [
            self.build(PixivStaccUrl, stacc_id=self.artist_data["user_account"])
        ]

        if user_webpage := self.artist_data.get("user_webpage"):
            urls.append(self.parse(user_webpage))

        if social_data := self.artist_data["social"]:
            for url_dict in social_data.values():
                urls.append(self.parse(url_dict[Url]))

        return urls

    @settable_property
    def is_deleted(self) -> bool:
        if not self.artist_data.get("error"):
            return False

        if self.artist_data["message"] in ["This user account has been suspended.",
                                           "User has left pixiv or the user ID does not exist.",]:
            return True

        raise NotImplementedError(self.artist_data["message"])


class PixivMeUrl(RedirectUrl, PixivUrl):
    domains = ["pixiv.me"]
    id_name = "me_id"
    patterns = {ME_PATTERN: "https://pixiv.me/{me_id}"}


class PixivStaccUrl(InfoUrl, PixivUrl):
    domains = ["pixiv.net"]
    id_name = "stacc_id"
    patterns = {STACC_PATTERN: "https://www.pixiv.net/stacc/{stacc_id}"}

    @property
    def me_from_stacc(self) -> PixivMeUrl:
        return self.build(PixivMeUrl, me_id=self.id)

    @property
    def related(self) -> list[Url]:
        return [self.me_from_stacc.resolved]

    @settable_property
    def is_deleted(self) -> bool:
        return self.me_from_stacc.is_deleted

    @property
    def names(self) -> list[str]:
        return [self.id]
