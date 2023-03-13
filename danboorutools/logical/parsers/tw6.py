from danboorutools.logical.extractors.tw6 import Tw6ArtistUrl, Tw6CharacterUrl, Tw6ImageUrl, Tw6PostUrl, Tw6Url
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class Tw6JpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Tw6Url | None:
        instance: Tw6Url
        match parsable_url.url_parts:

            # https://tw6.jp/gallery/master/?master_id=5344
            case "gallery", "master":
                instance = Tw6ArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.query["master_id"])

            # https://tw6.jp/gallery/?id=135910
            case "gallery", :
                instance = Tw6PostUrl(parsable_url)
                instance.post_id = int(parsable_url.query["id"])

            # https://tw6.jp/gallery/combine/6003  # redirects to image instead of posts
            case "gallery", "combine", post_id:
                instance = Tw6PostUrl(parsable_url)
                instance.post_id = int(post_id)

            # https://cdn.tw6.jp/i/tw6/basic/0167/920972_f01674_totalbody.jpg
            # https://cdn.tw6.jp/i/tw6/origin/3135/1085611_f31358_totalbody.png
            # https://cdn.tw6.jp/i/tw6/combined_origin/0258/1185475_f02583_totalbody.jpg
            case "i", "tw6", ("basic" | "origin" | "combined_origin"), _, _:  # no idea what the difference is
                instance = Tw6ImageUrl(parsable_url)

            # https://tw6.jp/character/status/f01521
            case "character", "status", character_id:
                instance = Tw6CharacterUrl(parsable_url)
                instance.character_id = character_id

            case _:
                return None

        return instance
