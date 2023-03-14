from danboorutools.logical.extractors.privatter import PrivatterArtistUrl, PrivatterImageUrl, PrivatterPostUrl, PrivatterUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class PrivatterNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PrivatterUrl | None:
        instance: PrivatterUrl
        match parsable_url.url_parts:
            # https://privatter.net/u/uzura_55
            # https://privatter.net/m/naoaraaa04
            case ("u" | "m"),  username:
                instance = PrivatterArtistUrl(parsable_url)
                instance.username = username

            # https://privatter.net/p/7115845
            # http://privatter.net/i/2655076
            case ("p" | "i") as post_type, post_id:
                instance = PrivatterPostUrl(parsable_url)
                instance.post_id = int(post_id)
                instance.post_type = post_type

            # http://privatter.net/img_original/856121876520129d361c6e.jpg
            case "img_original", _:
                instance = PrivatterImageUrl(parsable_url)

            case _:
                return None

        return instance
