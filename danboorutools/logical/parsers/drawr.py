from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.drawr import DrawrArtistUrl, DrawrImageUrl, DrawrPostUrl, DrawrUrl


class DrawrNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DrawrUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case "draw", "img", *_:
                return DrawrImageUrl(parsed_url=parsable_url)

            # http://drawr.net/show.php?id=626397#rid1218652
            # http://drawr.net/show.php?id=626397
            case "show.php", :
                return DrawrPostUrl(parsed_url=parsable_url,
                                    post_id=int(parsable_url.query["id"].split("#")[0]))

            case username, if not username.endswith(".php"):
                return DrawrArtistUrl(parsed_url=parsable_url,
                                      username=username)

            case _:
                return None
