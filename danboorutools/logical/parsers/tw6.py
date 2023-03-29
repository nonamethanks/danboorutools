from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.tw6 import Tw6ArtistUrl, Tw6CharacterUrl, Tw6ImageUrl, Tw6PostUrl, Tw6Url


class Tw6JpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Tw6Url | None:
        match parsable_url.url_parts:

            # https://tw6.jp/gallery/master/?master_id=5344
            case "gallery", "master":
                return Tw6ArtistUrl(parsed_url=parsable_url,
                                    user_id=int(parsable_url.query["master_id"]))

            # https://tw6.jp/gallery/?id=135910
            case "gallery", :
                return Tw6PostUrl(parsed_url=parsable_url,
                                  post_id=int(parsable_url.query["id"]))

            # https://tw6.jp/gallery/combine/6003  # redirects to image instead of posts
            case "gallery", "combine", post_id:
                return Tw6PostUrl(parsed_url=parsable_url,
                                  post_id=int(post_id))

            # https://cdn.tw6.jp/i/tw6/basic/0167/920972_f01674_totalbody.jpg
            # https://cdn.tw6.jp/i/tw6/origin/3135/1085611_f31358_totalbody.png
            # https://cdn.tw6.jp/i/tw6/combined_origin/0258/1185475_f02583_totalbody.jpg
            case "i", "tw6", ("basic" | "origin" | "combined_origin"), _, _:  # no idea what the difference is
                return Tw6ImageUrl(parsed_url=parsable_url)

            # https://tw6.jp/character/status/f01521
            case "character", "status", character_id:
                return Tw6CharacterUrl(parsed_url=parsable_url,
                                       character_id=character_id)

            case _:
                return None
