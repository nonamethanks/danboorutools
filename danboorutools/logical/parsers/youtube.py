from __future__ import annotations

from typing import TYPE_CHECKING

from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors import youtube as yt
from danboorutools.logical.parsers import ParsableUrl, UrlParser

if TYPE_CHECKING:
    from danboorutools.models.url import Url


class YoutubeComParser(UrlParser):
    RESERVED_NAMES = {"feed", "shorts", "gaming", "premium", "kids", "music", "help", "playlist", "live", "redirect"}

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Url | None:
        instance: yt.YoutubeUrl
        match parsable_url.url_parts:
            # http://www.youtube.com/watch?v=qi6EePWYZlQ\u0026fmt=18
            case "watch", :
                instance = yt.YoutubeVideoUrl(parsable_url)
                instance.video_id = parsable_url.query["v"]

            # https://www.youtube.com/shorts/gPSQPvxmGPA
            case "shorts", video_id:
                instance = yt.YoutubeVideoUrl(parsable_url)
                instance.video_id = video_id

            # https://www.youtube.com/c/kurasawakyosyo
            # https://www.youtube.com/user/speedosausage
            case ("user" | "c") as subdir, username, *_rest:
                instance = yt.YoutubeOldUserUrl(parsable_url)
                instance.username = username
                instance.subdir = subdir

            # https://www.youtube.com/@kyosyo/featured
            case username, *_rest if username.startswith("@"):
                instance = yt.YoutubeUserUrl(parsable_url)
                instance.username = username.removeprefix("@")

            # https://www.youtube.com/channel/UCMMBGMjrrWcRZmG_lW4jC-Q/community?lb=UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL
            case "channel", channel_id, "community" if parsable_url.query["lb"]:
                instance = yt.YoutubeCommunityPostUrl(parsable_url)
                instance.post_id = parsable_url.query["lb"]
                instance.channel_id = channel_id

            # https://www.youtube.com/channel/UC-v9d2zDU1Bjshz3r3CDhUA
            case "channel", channel_id, *_:
                instance = yt.YoutubeChannelUrl(parsable_url)
                instance.channel_id = channel_id

            # https://www.youtube.com/post/UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL
            case "post", post_id:
                instance = yt.YoutubeCommunityPostUrl(parsable_url)
                instance.post_id = post_id

            case "profile", :  # /profile urls are dead
                raise UnparsableUrl(parsable_url)

            # https://img.youtube.com/vi/vTPq-9k0m3A/maxresdefault.jpg
            case "vi", video_id, "maxresdefault.jpg":
                instance = yt.YoutubeVideoUrl(parsable_url)  # TODO: maybe YoutubeThumbnailUrl?
                instance.video_id = video_id

            case "playlist", :
                raise UnparsableUrl(parsable_url)

            # https://www.youtube.com/redirect?event=channel_description&redir_token=QUFFLUhqbmhHUm1HcUowbk8wUEJVZWJpWmRfck5yRUhWUXxBQ3Jtc0tuankwTXo2TTRYMFJNdDNwbnpUZ193Vk45b3FCVGxMcDNva1Rzby1wT1J1YUZpdTFRN0RvallTN0xwYUxYQXNWS1dvNU5wRExpZ0FBT2xxUTlUOGJ4TFNpcGptQ2xoVHpaUmtWTVI2WWhlNFhSZ1hEVQ&q=https%3A%2F%2Fwww.pixiv.net%2Fusers%2F37422
            case "redirect", :
                return cls.parse(parsable_url.query["q"])

            case reserved, *_ if reserved in cls.RESERVED_NAMES and parsable_url.subdomain in ["www", ""]:
                raise UnparsableUrl(parsable_url)

            case username, if parsable_url.subdomain in ["www", ""]:
                instance = yt.YoutubeUserUrl(parsable_url)
                instance.username = username

            case _:
                return None

        return instance
