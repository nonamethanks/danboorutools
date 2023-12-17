from typing import Literal

from danboorutools.logical.sessions.bilibili import BilibiliSession, BilibiliUserData
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class BilibiliUrl(Url):
    session = BilibiliSession()


class BilibiliVideoPostUrl(PostUrl, BilibiliUrl):
    video_id: str

    normalize_template = "https://www.bilibili.com/video/{video_id}"


class BilibiliPostUrl(PostUrl, BilibiliUrl):
    post_id: int
    post_type: Literal["h", "t"]

    normalize_template = "https://{post_type}.bilibili.com/{post_id}"


class BilibiliLiveUrl(PostUrl, BilibiliUrl):
    live_id: int

    normalize_template = "https://live.bilibili.com/{live_id}"


class BilibiliArticleUrl(PostUrl, BilibiliUrl):
    article_id: int

    normalize_template = "https://www.bilibili.com/read/cv{article_id}"


class BilibiliArtistUrl(ArtistUrl, BilibiliUrl):
    user_id: int

    normalize_template = "https://space.bilibili.com/{user_id}"

    @property
    def artist_data(self) -> BilibiliUserData:
        try:
            return self.session.user_data(user_id=self.user_id)
        except NotImplementedError as e:
            e.add_note(f"On {self}")
            raise

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.name]

    @property
    def secondary_names(self) -> list[str]:
        return [f"bilibili {self.user_id}"]

    @property
    def related(self) -> list[Url]:
        return []


class BilibiliImageUrl(PostAssetUrl, BilibiliUrl):
    user_id: str | None

    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query.split("@")[0]
