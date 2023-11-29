from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urljoin

from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import youtube as yt
from danboorutools.models.url import UselessUrl

if TYPE_CHECKING:
    from danboorutools.models.url import Url


class YoutubeComParser(UrlParser):
    RESERVED_NAMES = {"feed", "shorts", "gaming", "premium", "kids", "music", "help", "live", "redirect", "results"}

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Url | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # http://www.youtube.com/watch?v=qi6EePWYZlQ\u0026fmt=18
            case "watch", :
                return yt.YoutubeVideoUrl(parsed_url=parsable_url,
                                          video_id=parsable_url.query["v"])

            # https://www.youtube.com/shorts/gPSQPvxmGPA
            case "shorts", video_id:
                return yt.YoutubeVideoUrl(parsed_url=parsable_url,
                                          video_id=video_id)

            # https://www.youtube.com/c/kurasawakyosyo
            # https://www.youtube.com/user/speedosausage
            case ("user" | "c") as subdir, username, *_rest:
                return yt.YoutubeOldUserUrl(parsed_url=parsable_url,
                                            username=username,
                                            subdir=subdir)

            # https://www.youtube.com/channel/UCMMBGMjrrWcRZmG_lW4jC-Q/community?lb=UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL
            case "channel", channel_id, "community" if parsable_url.query["lb"]:
                return yt.YoutubeCommunityPostUrl(parsed_url=parsable_url,
                                                  post_id=parsable_url.query["lb"],
                                                  channel_id=channel_id)

            # https://www.youtube.com/channel/UC-v9d2zDU1Bjshz3r3CDhUA
            # http://youtube.com/@channel/UCxw3WZ7N63dYExDwbZbHvqg (broken url, found in behance)
            case ("channel" | "@channel"), channel_id, *_:
                return yt.YoutubeChannelUrl(parsed_url=parsable_url,
                                            channel_id=channel_id)

            # https://www.youtube.com/@kyosyo/featured
            case username, *_rest if username.startswith("@"):
                return yt.YoutubeUserUrl(parsed_url=parsable_url,
                                         username=username.removeprefix("@"))

            # https://www.youtube.com/post/UgkxWkFtKkCgWnCoPBWsMVzEYhm3ddURD0lL
            case "post", post_id:
                return yt.YoutubeCommunityPostUrl(parsed_url=parsable_url,
                                                  post_id=post_id)

            case "profile", :  # /profile urls are dead
                raise UnparsableUrlError(parsable_url)

            # https://img.youtube.com/vi/vTPq-9k0m3A/maxresdefault.jpg
            case "vi", video_id, "maxresdefault.jpg":
                return yt.YoutubeVideoUrl(parsed_url=parsable_url, video_id=video_id)  # TODO: maybe YoutubeThumbnailUrl?

            case "playlist", :
                playlist_id = parsable_url.query.get("list") or parsable_url.query.get("p")
                if not playlist_id:
                    raise NotImplementedError(parsable_url)
                return yt.YoutubePlaylistUrl(parsed_url=parsable_url, playlist_id=playlist_id)

            # https://www.youtube.com/redirect?event=channel_description&redir_token=QUFFLUhqbmhHUm1HcUowbk8wUEJVZWJpWmRfck5yRUhWUXxBQ3Jtc0tuankwTXo2TTRYMFJNdDNwbnpUZ193Vk45b3FCVGxMcDNva1Rzby1wT1J1YUZpdTFRN0RvallTN0xwYUxYQXNWS1dvNU5wRExpZ0FBT2xxUTlUOGJ4TFNpcGptQ2xoVHpaUmtWTVI2WWhlNFhSZ1hEVQ&q=https%3A%2F%2Fwww.pixiv.net%2Fusers%2F37422
            case "redirect", :
                query_url = parsable_url.query["q"]
                if not query_url.startswith("http"):
                    query_url = f"https://{query_url}"
                return cls.parse(query_url)

            case "m", if parsable_url.subdomain == "consent":
                return cls.parse(parsable_url.query["continue"])

            case reserved, *_ if reserved in cls.RESERVED_NAMES and parsable_url.subdomain in ["www", ""]:
                return UselessUrl(parsed_url=parsable_url)

            case username, if parsable_url.subdomain in ["www", ""]:
                return yt.YoutubeUserUrl(parsed_url=parsable_url,
                                         username=username)

            case _:
                return None


class YoutuBeParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> yt.YoutubeUrl | None:
        match parsable_url.url_parts:
            # http://youtu.be/fb90cRgI_ZQ
            case video_id, :
                return yt.YoutubeVideoUrl(parsed_url=parsable_url,
                                          video_id=video_id)

            case _:
                return None
