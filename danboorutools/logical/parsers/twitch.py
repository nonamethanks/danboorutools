from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.twitch import TwitchChannelUrl, TwitchUrl, TwitchVideoUrl


class TwitchTvParser(UrlParser):
    domains = ("twitch.tv", "twitch.com")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> TwitchUrl | None:
        match parsable_url.url_parts:
            # https://www.twitch.tv/videos/891413875
            case "videos", video_id:
                return TwitchVideoUrl(parsed_url=parsable_url,
                                      video_id=int(video_id))

            # https://www.twitch.tv/zxidart
            case username, :
                return TwitchChannelUrl(parsed_url=parsable_url,
                                        username=username)

            # https://www.twitch.tv/zxidart/profile
            case username, ("videos" | "profile" | "about" | "home" | "schedule"):
                return TwitchChannelUrl(parsed_url=parsable_url,
                                        username=username)

            case _:
                return None
