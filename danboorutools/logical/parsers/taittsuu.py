from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.taittsuu import TaittsuuArtistUrl, TaittsuuPostUrl
from danboorutools.models.url import Url, UselessUrl


class TaittsuuComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:
            case "users", username:
                return TaittsuuArtistUrl(parsed_url=parsable_url,
                                         username=username)
            case "users", username, "profiles":
                return TaittsuuArtistUrl(parsed_url=parsable_url,
                                         username=username)
            case "users", username, "status", post_id:
                return TaittsuuPostUrl(parsed_url=parsable_url,
                                       username=username,
                                       post_id=int(post_id))
            case "home", :
                return UselessUrl(parsable_url)
            case _:
                return None
