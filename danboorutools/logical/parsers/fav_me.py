from danboorutools.logical.extractors.deviantart import DeviantArtPostUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class FavMeParser(UrlParser):
    test_cases = {
        DeviantArtPostUrl: [
            "https://fav.me/dbc3a48",
            "https://www.fav.me/dbc3a48",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DeviantArtPostUrl | None:
        instance = DeviantArtPostUrl(parsable_url)
        instance.deviation_id = int(parsable_url.url_parts[0], 36)
        instance.title = None
        instance.username = None
        return instance
