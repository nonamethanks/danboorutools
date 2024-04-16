from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.inprnt import InprntArtistUrl, InprntImageUrl, InprntPostUrl, InprntUrl


class InprntComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> InprntUrl | None:
        match parsable_url.url_parts:
            case ("gallery" | "profile"), username, :
                return InprntArtistUrl(parsed_url=parsable_url,
                                       username=username)
            case "gallery", username, post_title:
                return InprntPostUrl(parsed_url=parsable_url,
                                     username=username,
                                     post_title=post_title)
            case "discover", "image", username, post_title:
                return InprntPostUrl(parsed_url=parsable_url,
                                     username=username,
                                     post_title=post_title)

            case "thumbs", _f1, _f2, _hash if parsable_url.subdomain == "cdn":
                return InprntImageUrl(parsed_url=parsable_url)

            case _:
                return None
