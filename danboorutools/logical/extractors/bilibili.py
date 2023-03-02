from typing import Literal

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class BilibiliUrl(Url):
    pass


class BilibiliVideoPostUrl(PostUrl, BilibiliUrl):
    video_id: str

    normalize_string = "https://www.bilibili.com/video/{video_id}"


class BilibiliPostUrl(PostUrl, BilibiliUrl):
    post_id: int
    post_type: Literal["h", "t"]

    normalize_string = "https://{post_type}.bilibili.com/{post_id}"


class BilibiliLiveUrl(PostUrl, BilibiliUrl):
    live_id: int

    normalize_string = "https://live.bilibili.com/{live_id}"


class BilibiliArticleUrl(PostUrl, BilibiliUrl):
    article_id: int

    normalize_string = "https://www.bilibili.com/read/cv{article_id}"


class BilibiliArtistUrl(ArtistUrl, BilibiliUrl):
    user_id: int

    normalize_string = "https://space.bilibili.com/{user_id}"


class BilibiliImageUrl(PostAssetUrl, BilibiliUrl):
    user_id: str | None

    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query
