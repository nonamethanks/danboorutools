from danboorutools.logical.sessions.weibo import WeiboSession, WeiboUserData
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class WeiboUrl(Url):
    session = WeiboSession()


class WeiboPostUrl(PostUrl, WeiboUrl):
    illust_long_id: int | None = None
    illust_base62_id: str | None = None
    artist_short_id: int | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if (artist_short_id := kwargs.get("artist_short_id")) and (illust_base62_id := kwargs.get("illust_base62_id")):
            return f"https://www.weibo.com/{artist_short_id}/{illust_base62_id}"
        elif (illust_long_id := kwargs.get("illust_long_id")):
            return f"https://www.weibo.com/detail/{illust_long_id}"
        elif (illust_base62_id := kwargs.get("illust_base62_id")):
            return f"https://m.weibo.cn/status/{illust_base62_id}"
        else:
            raise NotImplementedError


class WeiboArtistUrl(ArtistUrl, WeiboUrl):
    artist_short_id: int | None = None
    artist_long_id: int | None = None
    username: str | None = None
    screen_name: str | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if artist_short_id := kwargs.get("artist_short_id"):
            return f"https://www.weibo.com/u/{artist_short_id}"
        elif artist_long_id := kwargs.get("artist_long_id"):
            return f"https://www.weibo.com/p/{artist_long_id}"
        elif screen_name := kwargs.get("screen_name"):
            return f"https://www.weibo.com/n/{screen_name}"
        elif username := kwargs.get("username"):
            return f"https://www.weibo.com/{username}"
        else:
            raise NotImplementedError

    @property
    def artist_data(self) -> WeiboUserData:
        return self.session.user_data(
            short_id=self.artist_short_id,
            long_id=self.artist_long_id,
            username=self.username,
            screen_name=self.screen_name,
        )

    @property
    def primary_names(self) -> list[str]:
        names = []
        if self.screen_name:
            names += [self.screen_name]
        if self.artist_data.screen_name:
            names += [self.artist_data.screen_name]
        return list(set(names))

    @property
    def secondary_names(self) -> list[str]:
        names = []
        if self.username:
            names += [self.username]
        if self.artist_data.domain and not self.artist_data.domain.isnumeric():
            names += [self.artist_data.domain]
        return list(set(names))

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls


class WeiboImageUrl(PostAssetUrl, WeiboUrl):
    @property
    def full_size(self) -> str:
        if self.parsed_url.extension:
            return f"https://{self.parsed_url.hostname}/large/{self.parsed_url.filename}"
        else:
            raise NotImplementedError(self)

    # TODO: dead images redirect to https://image2.sina.com.cn/blog/tmpl/v3/images/default_s_bmiddle.gif or some shit
