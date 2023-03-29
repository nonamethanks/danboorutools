from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.gamer_tw import GamerTwArtistUrl, GamerTwForumPostUrl, GamerTwGnnPostUrl, GamerTwPostUrl, GamerTwUrl
from danboorutools.models.url import UselessUrl


class GamerComTwParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> GamerTwUrl | UselessUrl | None:
        if parsable_url.subdomain == "home":
            return cls._match_home(parsable_url)
        elif parsable_url.subdomain == "forum":
            return cls._match_forum(parsable_url)
        elif parsable_url.subdomain == "gnn":
            return cls._match_gnn(parsable_url)
        elif parsable_url.subdomain == "m":
            # https://m.gamer.com.tw/forum/C.php?bsn=34173\u0026snA=5731
            updated_url = f"https://{parsable_url.url_parts[0]}.gamer.com.tw/" + "/".join(parsable_url.raw_url.split("/")[4:])
            return cls.match_url(ParsableUrl(updated_url))
        else:
            return None

    @staticmethod
    def _match_home(parsable_url: ParsableUrl) -> GamerTwUrl | UselessUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://home.gamer.com.tw/homeindex.php?owner=her682913
            # http://home.gamer.com.tw/home.php?owner=ader0fabill
            # https://home.gamer.com.tw/creation.php?owner=lcomicer
            case ("homeindex.php" | "home.php" | "creation.php"), :
                if not parsable_url.query:
                    return UselessUrl(parsed_url=parsable_url)
                return GamerTwArtistUrl(parsed_url=parsable_url,
                                        artist_id=parsable_url.query["owner"])

            # https://home.gamer.com.tw/creationDetail.php?sn=2824881
            # https://home.gamer.com.tw/artwork.php?sn=5245406
            case ("creationDetail.php" | "artwork.php"), :
                return GamerTwPostUrl(parsed_url=parsable_url,
                                      post_id=int(parsable_url.query["sn"]))

            case artist_id, if not artist_id.endswith(".php"):
                return GamerTwArtistUrl(parsed_url=parsable_url,
                                        artist_id=artist_id)

            case _:
                return None

    @staticmethod
    def _match_forum(parsable_url: ParsableUrl) -> GamerTwUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://forum.gamer.com.tw/C.php?bsn=7650&snA=1024581
            # https://forum.gamer.com.tw/C.php?page=8\u0026bsn=36399\u0026snA=54
            # https://forum.gamer.com.tw/Co.php?bsn=31483\u0026sn=2108
            case subforum, if subforum.endswith(".php"):

                if "snA" in parsable_url.query:
                    sn_type = "snA"
                    sn = int(parsable_url.query["snA"])
                elif "sn" in parsable_url.query:
                    sn_type = "sn"
                    sn = int(parsable_url.query["sn"])
                else:
                    raise NotImplementedError(parsable_url)

                return GamerTwForumPostUrl(parsed_url=parsable_url,
                                           subforum=subforum,
                                           sn=sn,
                                           sn_type=sn_type,  # type: ignore[arg-type]
                                           bsn=int(parsable_url.query["bsn"]))

            case _:
                return None

    @staticmethod
    def _match_gnn(parsable_url: ParsableUrl) -> GamerTwUrl | None:
        match parsable_url.url_parts:
            # https://gnn.gamer.com.tw/detail.php?sn=190824
            case "detail.php", :
                return GamerTwGnnPostUrl(parsed_url=parsable_url,
                                         post_id=int(parsable_url.query["sn"]))

            case _:
                return None
