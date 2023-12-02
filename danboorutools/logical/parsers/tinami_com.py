from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.tinami import TinamiArtistUrl, TinamiComicUrl, TinamiImageUrl, TinamiPostUrl, TinamiUrl


class TinamiComParser(UrlParser):
    domains = ("tinami.com", "tinami.jp")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> TinamiUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case _ if parsable_url.subdomain == "img":
                return TinamiImageUrl(parsed_url=parsable_url)
            case "creator", "profile", user_id:
                return TinamiArtistUrl(parsed_url=parsable_url,
                                       user_id=int(user_id),
                                       profile_id=None)

            case "search", "list":
                return TinamiArtistUrl(parsed_url=parsable_url,
                                       user_id=int(parsable_url.query["prof_id"]),
                                       profile_id=None)

            case ("profile" | "p"), profile_id:
                return TinamiArtistUrl(parsed_url=parsable_url,
                                       profile_id=int(profile_id),
                                       user_id=None)

            case "view", *_, post_id:
                return TinamiPostUrl(parsed_url=parsable_url,
                                     post_id=int(post_id))

            case "comic", comic_title, comic_id:
                return TinamiComicUrl(parsed_url=parsable_url,
                                      comic_id=int(comic_id.removesuffix(".php")),
                                      comic_title=comic_title)

            # http://www.tinami.com/today/artworks/t071231_130617.jpg
            # http://www.tinami.com/gallery/img/34_eri_n.jpg
            case ("today" | "gallery"), *_:
                raise UnparsableUrlError(parsable_url)

            case _:
                return None
