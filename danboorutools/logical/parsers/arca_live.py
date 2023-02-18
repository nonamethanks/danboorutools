from danboorutools.logical.extractors.arca_live import ArcaLiveArtistUrl, ArcaLivePostUrl, ArcaLiveUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class ArcaLiveParser(UrlParser):
    test_cases = {
        ArcaLivePostUrl: [
            "https://arca.live/b/arknights/66031722",
        ],
        ArcaLiveArtistUrl: [
            "https://arca.live/u/@Si리링",
            "https://arca.live/u/@Nauju/45320365",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ArcaLiveUrl | None:
        instance: ArcaLiveUrl
        match parsable_url.url_parts:
            case "b", channel, post_id:
                instance = ArcaLivePostUrl(parsable_url)
                instance.post_id = int(post_id)
                instance.channel = channel
            case "u", username, user_id if username.startswith("@"):
                instance = ArcaLiveArtistUrl(parsable_url)
                instance.user_id = int(user_id)
                instance.username = username.removeprefix("@")
            case "u", username if username.startswith("@"):
                instance = ArcaLiveArtistUrl(parsable_url)
                instance.username = username.removeprefix("@")
                instance.user_id = None
            case _:
                return None
        return instance
