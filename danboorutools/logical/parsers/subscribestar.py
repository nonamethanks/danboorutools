from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.subscribestar import SubscribestarArtistUrl, SubscribestarPostUrl, SubscribestarUrl


class SubscribestarAdultParser(UrlParser):
    reserved = ("login", "signup", "password", "stars", "features", "pricing", "api", "about", "search",
                "tos", "privacy", "refund", "subscribestar-adult", "brand", "contacts", "guidelines", "help")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> SubscribestarUrl | None:
        match parsable_url.url_parts:
            # https://subscribestar.adult/everyday2
            case username, if username not in cls.reserved:
                return SubscribestarArtistUrl(parsed_url=parsable_url,
                                              username=username)

            # https://subscribestar.adult/posts/437146
            case "posts", post_id:
                return SubscribestarPostUrl(parsed_url=parsable_url,
                                            post_id=int(post_id))
            case _:
                return None
