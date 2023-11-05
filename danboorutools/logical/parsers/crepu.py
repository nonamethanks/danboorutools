from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.crepu import CrepuArtistUrl, CrepuPostUrl, CrepuUrl


class CrepuNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> CrepuUrl | None:
        match parsable_url.url_parts:
            case "user", username:
                return CrepuArtistUrl(parsed_url=parsable_url,
                                                  username=username)
            case "post", post_id:
                return CrepuPostUrl(parsed_url=parsable_url,
                                    post_id=int(post_id))
            case _:
                return None
