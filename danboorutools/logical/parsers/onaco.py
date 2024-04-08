from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.onaco import OnacoArtistUrl, OnacoImageUrl, OnacoPostUrl, OnacoUrl


class OnacoJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> OnacoUrl | None:
        match parsable_url.url_parts:
            case "profile", username, :
                return OnacoArtistUrl(parsed_url=parsable_url,
                                      username=username)
            case "detail", post_id, :
                return OnacoPostUrl(parsed_url=parsable_url,
                                    post_id=post_id)
            case _:
                return None
