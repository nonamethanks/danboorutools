from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.privatter import PrivatterArtistUrl, PrivatterImageUrl, PrivatterPostUrl, PrivatterUrl


class PrivatterNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PrivatterUrl | None:
        match parsable_url.url_parts:
            # https://privatter.net/u/uzura_55
            # https://privatter.net/m/naoaraaa04
            case ("u" | "m"),  username:
                return PrivatterArtistUrl(parsed_url=parsable_url,
                                          username=username)

            # https://privatter.net/p/7115845
            # http://privatter.net/i/2655076
            case ("p" | "i") as post_type, post_id:
                return PrivatterPostUrl(parsed_url=parsable_url,
                                        post_id=int(post_id),
                                        post_type=post_type)

            # http://privatter.net/img_original/856121876520129d361c6e.jpg
            case "img_original", _:
                return PrivatterImageUrl(parsed_url=parsable_url)

            case _:
                return None
