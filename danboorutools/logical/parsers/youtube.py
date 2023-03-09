from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors import youtube as yt
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class YoutubeComParser(UrlParser):
    RESERVED_NAMES = {"feed", "shorts", "gaming", "premium", "kids", "music", "help", "playlist", "live", }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> yt.YoutubeUrl | None:
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
                instance = yt.YoutubeVideoUrl(parsable_url) # TODO: maybe YoutubeThumbnailUrl?
                instance.video_id = video_id

            case reserved, *_ if reserved in cls.RESERVED_NAMES:
                raise UnparsableUrl(parsable_url)

            case username, :
                instance = yt.YoutubeUserUrl(parsable_url)
                instance.username = username

            case _:
                return None

        return instance
