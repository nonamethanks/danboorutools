from functools import cached_property
from typing import Literal

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions.youtube import YoutubeChannelData, YoutubeSession
from danboorutools.models.url import ArtistUrl, GalleryUrl, PostUrl, RedirectUrl, Url


class YoutubeUrl(Url):
    session = YoutubeSession()


class YoutubeUserUrl(ArtistUrl, YoutubeUrl):
    username: str

    normalize_template = "https://www.youtube.com/@{username}"

    @property
    def channel_data(self) -> YoutubeChannelData:
        return self.session.channel_data(self.normalized_url)

    @property
    def primary_names(self) -> list[str]:
        try:
            return [self.channel_data.title.strip()]
        except DeadUrlError:
            return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username] if not self.username.startswith("user-") else []

    @property
    def related(self) -> list[Url]:
        try:
            return self.channel_data.related_urls
        except DeadUrlError:
            return []


class YoutubeOldUserUrl(RedirectUrl, YoutubeUrl):
    username: str
    subdir: Literal["c", "user"]

    normalize_template = "https://www.youtube.com/{subdir}/{username}"
    # direcly normalizing is not always possible:
    # https://www.youtube.com/user/kurasawakyosyo   -> ok
    # https://www.youtube.com/c/kurasawakyosyo      -> 404
    # https://www.youtube.com/user/pixmilk-channel  -> 404
    # https://www.youtube.com/c/pixmilk-channel     -> ok


class YoutubeChannelUrl(RedirectUrl, YoutubeUrl):
    channel_id: str

    normalize_template = "https://www.youtube.com/channel/{channel_id}"

    @cached_property
    def resolved(self) -> Url:
        return self.channel_data.vanity_url

    @property
    def channel_data(self) -> YoutubeChannelData:
        return self.session.channel_data(self.normalized_url)


class YoutubeVideoUrl(PostUrl, YoutubeUrl):
    video_id: str
    normalize_template = "https://www.youtube.com/watch?v={video_id}"


class YoutubePlaylistUrl(GalleryUrl, YoutubeUrl):
    playlist_id: str
    normalize_template = "https://www.youtube.com/playlist?list={playlist_id}"


class YoutubeCommunityPostUrl(PostUrl, YoutubeUrl):
    post_id: str
    channel_id: str | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if channel_id := kwargs.get("channel_id"):
            return f"https://www.youtube.com/channel/{channel_id}/community?lb={kwargs["post_id"]}"
        else:
            return f"https://www.youtube.com/post/{kwargs["post_id"]}"
