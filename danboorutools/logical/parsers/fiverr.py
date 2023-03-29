import re

from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.fiverr import FiverrArtistUrl, FiverrPostUrl, FiverrShareUrl, FiverrUrl


class FiverrComParser(UrlParser):
    username_pattern = re.compile(r"^\w+$")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FiverrUrl | None:
        if not cls.username_pattern.match(parsable_url.url_parts[0]):
            return None

        match parsable_url.url_parts:
            case ("share" | "s2") as subdir, share_code:
                return FiverrShareUrl(parsed_url=parsable_url,
                                      subdir=subdir,
                                      share_code=share_code)

            case username, title:
                return FiverrPostUrl(parsed_url=parsable_url,
                                     artist_name=username,
                                     post_title=title)

            case username, :
                return FiverrArtistUrl(parsed_url=parsable_url,
                                       artist_name=username)

            case _:
                return None
