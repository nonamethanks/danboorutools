from danboorutools.logical.extractors.tw6 import Tw6ArtistUrl, Tw6Url
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class Tw6JpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Tw6Url | None:
        match parsable_url.url_parts:
            case "gallery", "master":
                instance = Tw6ArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.query["master_id"])
            case _:
                return None

        return instance
