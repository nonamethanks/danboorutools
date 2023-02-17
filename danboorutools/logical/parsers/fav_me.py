from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.strategies.deviantart import FavMeUrl


class FavMeParser(UrlParser):
    test_cases = {
        FavMeUrl: [
            "https://fav.me/dbc3a48",
            "https://www.fav.me/dbc3a48",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FavMeUrl | None:
        instance = FavMeUrl(parsable_url.url)
        instance.favme_id = parsable_url.url_parts[0]
        return instance
