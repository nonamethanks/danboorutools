from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.wavebox import WaveboxUrl


class WaveboxMeParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> WaveboxUrl | None:
        match parsable_url.url_parts:
            case "wave", user_id:
                return WaveboxUrl(parsed_url=parsable_url,
                                  user_id=user_id)
            case _:
                return None
