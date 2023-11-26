from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.throne import ThroneArtistUrl, ThronePostUrl, ThroneUrl


class ThroneComParser(UrlParser):

    domains = ("throne.com", "jointhrone.com")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ThroneUrl | None:
        match parsable_url.url_parts:
            case username, "wishlist":
                return ThroneArtistUrl(parsed_url=parsable_url,
                                       username=username)

            # https://jointhrone.com/u/brittanybabbles
            case "u", username, :
                return ThroneArtistUrl(parsed_url=parsable_url,
                                       username=username)

            # https://throne.com/brittanybabbles
            case username, :
                return ThroneArtistUrl(parsed_url=parsable_url,
                                       username=username)

            # https://throne.com/brittanybabbles/item/aee67ff0-c78c-4ffa-879a-40d9f6eee670
            case username, "item", post_id:
                return ThronePostUrl(parsed_url=parsable_url,
                                     username=username,
                                     post_id=post_id)

            case _:
                return None
