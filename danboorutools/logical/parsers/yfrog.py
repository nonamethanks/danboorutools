import re

from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.yfrog import YfrogArtistUrl, YfrogImageUrl, YfrogPostUrl, YfrogUrl
from danboorutools.models.url import UnsupportedUrl


class YfrogComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> YfrogUrl | UnsupportedUrl | None:
        if parsable_url.subdomain == "a" or re.match(r"img\d*", parsable_url.subdomain):
            return YfrogImageUrl(parsed_url=parsable_url)

        if parsable_url.subdomain == "twitter":
            return UnsupportedUrl(parsed_url=parsable_url)

        match parsable_url.url_parts:
            case "user", username, "photos", :
                return YfrogArtistUrl(parsed_url=parsable_url,
                                      username=username)
            case post_id, :
                return YfrogPostUrl(parsed_url=parsable_url,
                                    post_id=post_id)
            case _:
                return None
