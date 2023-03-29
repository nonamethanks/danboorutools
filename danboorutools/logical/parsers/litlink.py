from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.litlink import LitlinkUrl


class LitLinkParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> LitlinkUrl | None:
        match parsable_url.url_parts:
            case "en", username:
                return LitlinkUrl(parsed_url=parsable_url,
                                  username=username)

            case username, :
                return LitlinkUrl(parsed_url=parsable_url,
                                  username=username)

            case _:
                return None
