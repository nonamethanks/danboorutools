from danboorutools.logical.extractors.newgrounds import NewgroundsImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class UngroundedNetParser(UrlParser):
    test_cases = {
        NewgroundsImageUrl: [
            "https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.1080p.mp4?1639666238",
            "https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.720p.mp4?1639666238",
            "https://uploads.ungrounded.net/alternate/1801000/1801343_alternate_165104.360p.mp4?1639666238",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> NewgroundsImageUrl | None:
        match parsable_url.url_parts:
            case "alternate", _, _:
                instance = NewgroundsImageUrl(parsable_url)
                instance.title = None
                instance.username = None
            case _:
                return None

        return instance
