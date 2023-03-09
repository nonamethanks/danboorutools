from typing import Literal

from danboorutools.models.url import ArtistUrl, PostUrl, RedirectUrl, Url


class YoutubeUrl(Url):
    pass


class YoutubeUserUrl(ArtistUrl, YoutubeUrl):
    username: str

    normalize_string = "https://www.youtube.com/@{username}"


class YoutubeOldUserUrl(RedirectUrl, YoutubeUrl):
    username: str
    subdir: Literal["c", "user"]

    normalize_string = "https://www.youtube.com/{subdir}/{username}"
    # direcly normalizing is not always possible:
    # https://www.youtube.com/user/kurasawakyosyo   -> ok
    # https://www.youtube.com/c/kurasawakyosyo      -> 404
    # https://www.youtube.com/user/pixmilk-channel  -> 404
    # https://www.youtube.com/c/pixmilk-channel     -> ok


class YoutubeChannelUrl(RedirectUrl, YoutubeUrl):
    channel_id: str

    normalize_string = "https://www.youtube.com/channel/{channel_id}"


class YoutubeVideoUrl(PostUrl, YoutubeUrl):
    video_id: str
    normalize_string = "https://www.youtube.com/watch?v={video_id}"


class YoutubeCommunityPostUrl(PostUrl, YoutubeUrl):
    post_id: str
    channel_id: str | None = None

    @classmethod
    def normalize(cls, **kwargs) -> str | None:
        if channel_id := kwargs.get("channel_id"):
            return f"https://www.youtube.com/channel/{channel_id}/community?lb={kwargs['post_id']}"
        else:
            return f"https://www.youtube.com/post/{kwargs['post_id']}"
