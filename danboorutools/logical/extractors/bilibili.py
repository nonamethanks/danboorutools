from typing import Literal

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class BilibiliUrl(Url):
    pass


class BilibiliVideoPostUrl(PostUrl, BilibiliUrl):
    video_id: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        video_id = kwargs["video_id"]
        return f"https://www.bilibili.com/video/{video_id}"


class BilibiliPostUrl(PostUrl, BilibiliUrl):
    post_id: int
    post_type: Literal["h", "t"]

    @classmethod
    def normalize(cls, **kwargs) -> str:
        post_id = kwargs["post_id"]
        post_type = kwargs["post_type"]
        return f"https://{post_type}.bilibili.com/{post_id}"


class BilibiliLiveUrl(PostUrl, BilibiliUrl):
    live_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        live_id = kwargs["live_id"]
        return f"https://live.bilibili.com/{live_id}"


class BilibiliArticleUrl(PostUrl, BilibiliUrl):
    article_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        article_id = kwargs["article_id"]
        return f"https://www.bilibili.com/read/cv{article_id}"


class BilibiliArtistUrl(ArtistUrl, BilibiliUrl):
    user_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        user_id = kwargs["user_id"]
        return f"https://space.bilibili.com/{user_id}"


class BilibiliImageUrl(PostAssetUrl, BilibiliUrl):
    user_id: str | None

    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_params
