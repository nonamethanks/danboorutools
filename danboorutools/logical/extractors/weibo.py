from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class WeiboUrl(Url):
    pass


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
    display_name: str | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if artist_short_id := kwargs.get("artist_short_id"):
            return f"https://www.weibo.com/u/{artist_short_id}"
        elif artist_long_id := kwargs.get("artist_long_id"):
            return f"https://www.weibo.com/p/{artist_long_id}"
        elif display_name := kwargs.get("display_name"):
            return f"https://www.weibo.com/n/{display_name}"
        elif username := kwargs.get("username"):
            return f"https://www.weibo.com/{username}"
        else:
            raise NotImplementedError


class WeiboImageUrl(PostAssetUrl, WeiboUrl):
    @property
    def full_size(self) -> str:
        if self.parsed_url.extension:
            return f"https://{self.parsed_url.hostname}/large/{self.parsed_url.filename}"
        else:
            raise NotImplementedError(self)

    # TODO: dead images redirect to https://image2.sina.com.cn/blog/tmpl/v3/images/default_s_bmiddle.gif or some shit
