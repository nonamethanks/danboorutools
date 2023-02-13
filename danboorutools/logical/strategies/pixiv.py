from datetime import datetime
from functools import cached_property

from danboorutools.logical.sessions.pixiv import PixivSession
from danboorutools.models.url import ArtistUrl, AssetUrl, InfoUrl, PostUrl, RedirectUrl, Url
from danboorutools.util.misc import compile_url, memoize, settable_property
from danboorutools.util.time import datetime_from_string

BASE_DOMAIN = compile_url(r"https?:\/\/(?:(?:www|touch)\.)?pixiv\.net")
POST_PATTERN = compile_url(BASE_DOMAIN, r"\/(?:en\/)?(member_illust\.php?.*?|artworks\/|i\/)(?P<post_id>\d+)")
ARTIST_PATTERN = compile_url(BASE_DOMAIN, r"\/(?:(?:novel\/)?member\.php\?id=|u|(?:en\/)?users?)\/?(?P<artist_id>\d+)")
IMAGE_PATTERN = compile_url(r"https?:\/\/i[\w-]*\.(?:pximg\.net|pixiv\.net)\/.*?img\/(?:(?:\d+\/){6}|\w+\/)(?P<post_id>\d+)[\w\.]+")

ME_PATTERN = compile_url(r"https?:\/\/(?:www\.)?pixiv\.me\/(?P<me_id>[^\/]+)")
STACC_PATTERN = compile_url(r"https?:\/\/(?:www\.)?pixiv(\.net\/stacc|\.cc)\/(?P<stacc_id>[^\/]+)\/?")


class PixivUrl(Url):  # pylint: disable=abstract-method
    session = PixivSession()
    domains = ["pixiv.net"]
    excluded_paths = ["sketch.pixiv.net/", "img-sketch.pixiv.net/"]


class PixivImageUrl(AssetUrl, PixivUrl):
    test_cases = [
        "https://i.pximg.net/img-original/img/2014/10/03/18/10/20/46324488_p0.png",
        "https://i.pximg.net/img-master/img/2014/10/03/18/10/20/46324488_p0_master1200.jpg",
        "https://i.pximg.net/c/250x250_80_a2/img-master/img/2014/10/29/09/27/19/46785915_p0_square1200.jpg",
        "https://i.pximg.net/img-zip-ugoira/img/2016/04/09/14/25/29/56268141_ugoira1920x1080.zip",
        "https://i.pximg.net/img-original/img/2019/05/27/17/59/33/74932152_ugoira0.jpg",
        "https://i.pximg.net/c/360x360_70/custom-thumb/img/2022/03/08/00/00/56/96755248_p0_custom1200.jpg",
        "https://i-f.pximg.net/img-original/img/2020/02/19/00/40/18/79584713_p0.png",
        "http://img18.pixiv.net/img/evazion/14901720.png",
        "http://i2.pixiv.net/img18/img/evazion/14901720.png",
        "http://i1.pixiv.net/img07/img/pasirism/18557054_p1.png",
        "http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_64x64.jpg",
        "http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_s.png",
    ]
    domains = ["pximg.net", "pixiv.net"]
    excluded_paths = ["img-sketch.pximg.net/"]
    id_name = "post_id"
    patterns = [IMAGE_PATTERN]

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
    test_cases = [
        "https://www.pixiv.net/en/artworks/46324488",
        "https://www.pixiv.net/artworks/46324488",
        "http://www.pixiv.net/i/18557054",
        "http://www.pixiv.net/member_illust.php?mode=medium&illust_id=18557054",
        "http://www.pixiv.net/member_illust.php?mode=big&illust_id=18557054",
        "http://www.pixiv.net/member_illust.php?mode=manga&illust_id=18557054",
        "http://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=18557054&page=1",
    ]
    id_name = "post_id"
    patterns = [POST_PATTERN]
    normalization = "https://www.pixiv.net/en/artworks/{post_id}"

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
    test_cases = [
        "https://www.pixiv.net/member.php?id=339253",
        "http://www.pixiv.net/novel/member.php?id=76567",
        "https://www.pixiv.net/u/9202877",
        "https://www.pixiv.net/users/9202877",
        "https://www.pixiv.net/users/76567/novels",
        "https://www.pixiv.net/users/39598149/illustrations?p=1",
        "https://www.pixiv.net/user/13569921/series/81967",
        "https://www.pixiv.net/en/users/9202877",
        "https://www.pixiv.net/en/users/76567/novels",
    ]
    id_name = "artist_id"
    patterns = [ARTIST_PATTERN]
    normalization = "https://www.pixiv.net/en/users/{artist_id}"

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
    # Useful to have separate from Stacc, to get the pixiv ID indirectly
    test_cases = [
        "http://www.pixiv.me/noizave",
    ]
    domains = ["pixiv.me"]
    id_name = "me_id"
    patterns = [ME_PATTERN]
    normalization = "https://pixiv.me/{me_id}"


class PixivStaccUrl(InfoUrl, PixivUrl):
    domains = ["pixiv.net", "pixiv.cc"]
    test_cases = [
        "https://www.pixiv.net/stacc/noizave",
        "https://pixiv.cc/zerousagi",
    ]
    id_name = "stacc_id"
    patterns = [STACC_PATTERN]
    normalization = "https://www.pixiv.net/stacc/{stacc_id}"

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
