from danboorutools.logical.extractors.drawr import DrawrArtistUrl, DrawrImageUrl, DrawrPostUrl, DrawrUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class DrawrNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DrawrUrl | None:
        instance: DrawrUrl
        match parsable_url.url_parts:
            case "draw", "img", *_:
                instance = DrawrImageUrl(parsable_url)

            # http://drawr.net/show.php?id=626397#rid1218652
            # http://drawr.net/show.php?id=626397
            case "show.php", :
                instance = DrawrPostUrl(parsable_url)
                instance.post_id = int(parsable_url.query["id"].split("#")[0])

            case username, if not username.endswith(".php"):
                instance = DrawrArtistUrl(parsable_url)
                instance.username = username
            case _:
                return None

        return instance
