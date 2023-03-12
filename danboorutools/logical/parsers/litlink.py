from danboorutools.logical.extractors.litlink import LitlinkUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class LitLinkParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> LitlinkUrl | None:
        match parsable_url.url_parts:
            case "en", username:
                instance = LitlinkUrl(parsable_url)
                instance.username = username
            case username, :
                instance = LitlinkUrl(parsable_url)
                instance.username = username
            case _:
                return None

        return instance
