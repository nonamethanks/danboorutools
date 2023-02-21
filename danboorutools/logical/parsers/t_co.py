from danboorutools.logical.extractors.twitter import TwitterShortenerUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class TCoParser(UrlParser):
    test_cases = {
        TwitterShortenerUrl: [
            "https://t.co/Dxn7CuVErW",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> TwitterShortenerUrl | None:
        match parsable_url.url_parts:
            case shortener_id, :
                instance = TwitterShortenerUrl(parsable_url)
                instance.shortener_id = shortener_id
            case _:
                return None

        return instance
