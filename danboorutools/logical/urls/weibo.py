from datetime import datetime
from functools import cached_property

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions.weibo import WeiboPostData, WeiboSession, WeiboUserData
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class WeiboUrl(Url):
    session = WeiboSession()


class WeiboArtistUrl(ArtistUrl, WeiboUrl):
    artist_id: int

    normalize_template = "https://www.weibo.com/u/{artist_id}"

    extra_primary_names: list | None = None
    extra_secondary_names: list | None = None

    @property
    def artist_data(self) -> WeiboUserData:
        return self.session.user_data(artist_id=self.artist_id)

    @property
    def primary_names(self) -> list[str]:
        names = self.extra_primary_names or []
        if not self.is_deleted and self.artist_data.screen_name:
            names += [self.artist_data.screen_name]
        return list(set(names))

    @property
    def secondary_names(self) -> list[str]:
        if self.extra_secondary_names:
            return list(set(self.extra_secondary_names))
        return [f"weibo {self.artist_id}"]

    @property
    def related(self) -> list[Url]:
        if self.is_deleted:
            return []
        return self.artist_data.related_urls


class WeiboLegacyArtistUrl(RedirectUrl, WeiboUrl):
    artist_long_id: int | None = None
    screen_name: str | None = None
    username: str | None = None

    @property
    def resolved(self) -> WeiboArtistUrl:
        url = self.normalized_url.replace("www.weibo.com", "m.weibo.cn")
        resolved_resp = self.session.get(f"{url}?&jumpfrom=weibocom")
        resolved = resolved_resp.url

        if isinstance(parsed_resolved := Url.parse(resolved), WeiboLegacyArtistUrl) and parsed_resolved.username == self.username:
            raise DeadUrlError(resolved_resp)

        parsed = WeiboArtistUrl.parse_and_assert(resolved)
        if self.screen_name:
            parsed.extra_primary_names = [self.screen_name]
        if self.username:
            parsed.extra_secondary_names = [self.username]
        return parsed

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if artist_long_id := kwargs.get("artist_long_id"):
            return f"https://www.weibo.com/p/{artist_long_id}"
        elif screen_name := kwargs.get("screen_name"):
            return f"https://www.weibo.com/n/{screen_name}"
        elif username := kwargs.get("username"):
            return f"https://www.weibo.com/{username}"
        else:
            raise NotImplementedError


class WeiboPostUrl(PostUrl, WeiboUrl):
    illust_long_id: int | None = None
    illust_base62_id: str | None = None
    artist_id: int | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if (artist_id := kwargs.get("artist_id")) and (illust_base62_id := kwargs.get("illust_base62_id")):
            return f"https://www.weibo.com/{artist_id}/{illust_base62_id}"
        elif (illust_long_id := kwargs.get("illust_long_id")):
            return f"https://www.weibo.com/detail/{illust_long_id}"
        elif (illust_base62_id := kwargs.get("illust_base62_id")):
            return f"https://m.weibo.cn/status/{illust_base62_id}"
        else:
            raise NotImplementedError

    @property
    def post_data(self) -> WeiboPostData:
        if self.illust_base62_id:
            return self.session.post_data(base_62_id=self.illust_base62_id)
        elif self.illust_long_id:
            return self.session.post_data(long_id=self.illust_long_id)
        else:
            raise ValueError

    @cached_property
    def gallery(self) -> WeiboArtistUrl:
        if self.artist_id:
            return WeiboArtistUrl.build(artist_id=self.artist_id)
        return WeiboArtistUrl.build(artist_id=self.post_data.user.id)

    @cached_property
    def created_at(self) -> datetime:
        return self.post_data.created_at

    @cached_property
    def is_deleted(self) -> bool:
        try:
            _ = self.post_data
        except DeadUrlError:
            return True
        else:
            return False


class WeiboImageUrl(PostAssetUrl, WeiboUrl):
    @property
    def full_size(self) -> str:
        if self.parsed_url.extension:
            return f"https://{self.parsed_url.hostname}/large/{self.parsed_url.filename}"
        else:
            raise NotImplementedError(self)

    # TODO: dead images redirect to https://image2.sina.com.cn/blog/tmpl/v3/images/default_s_bmiddle.gif or some shit
