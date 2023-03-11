import re

from danboorutools.logical.extractors.fiverr import FiverrArtistUrl, FiverrPostUrl, FiverrShareUrl, FiverrUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class FiverrComParser(UrlParser):
    username_pattern = re.compile(r"^\w+$")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FiverrUrl | None:
        instance: FiverrUrl

        if not cls.username_pattern.match(parsable_url.url_parts[0]):
            return None

        match parsable_url.url_parts:
            case ("share" | "s2") as subdir, share_code:
                instance = FiverrShareUrl(parsable_url)
                instance.subdir = subdir
                instance.share_code = share_code
            case username, title:
                instance = FiverrPostUrl(parsable_url)
                instance.artist_name = username
                instance.post_title = title
            case username, :
                instance = FiverrArtistUrl(parsable_url)
                instance.artist_name = username
            case _:
                return None

        return instance
