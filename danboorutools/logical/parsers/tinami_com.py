from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.tinami import TinamiArtistUrl, TinamiComicUrl, TinamiImageUrl, TinamiPostUrl, TinamiUrl


class TinamiComParser(UrlParser):
    domains = ["tinami.com", "tinami.jp"]
    test_cases = {
        TinamiArtistUrl: [
            "http://www.tinami.com/creator/profile/1624",
            "https://www.tinami.com/search/list?prof_id=1624",


            "http://www.tinami.com/profile/1182",  # (creator: http://www.tinami.com/creator/profile/1624)
            "http://www.tinami.jp/p/1182",
        ],
        TinamiImageUrl: [
            "https://img.tinami.com/illust/img/287/497c8a9dc60e6.jpg",
            "https://img.tinami.com/illust2/img/419/5013fde3406b9.jpg",  # (page: https://www.tinami.com/view/461459)
            "https://img.tinami.com/illust2/L/452/622f7aa336bf3.gif",  # (thumbnail)",
            "https://img.tinami.com/comic/naomao/naomao_001_01.jpg",  # (page: http://www.tinami.com/comic/naomao/1)
            "https://img.tinami.com/comic/naomao/naomao_002_01.jpg",  # (page: http://www.tinami.com/comic/naomao/2)
            "https://img.tinami.com/comic/naomao/naomao_topillust.gif",
        ],
        TinamiPostUrl: [
            "https://www.tinami.com/view/461459",
            "https://www.tinami.com/view/tweet/card/461459",
        ],
        TinamiComicUrl: [
            "http://www.tinami.com/comic/naomao/2",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> TinamiUrl | None:
        instance: TinamiUrl

        match parsable_url.url_parts:
            case _ if parsable_url.subdomain == "img":
                instance = TinamiImageUrl(parsable_url)
            case "creator", "profile", user_id:
                instance = TinamiArtistUrl(parsable_url)
                instance.user_id = int(user_id)
                instance.profile_id = None
            case "search", "list":
                instance = TinamiArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.query["prof_id"])
                instance.profile_id = None
            case ("profile" | "p"), profile_id:
                instance = TinamiArtistUrl(parsable_url)
                instance.profile_id = int(profile_id)
                instance.user_id = None
            case "view", *_, post_id:
                instance = TinamiPostUrl(parsable_url)
                instance.post_id = int(post_id)
            case "comic", comic_title, comic_id:
                instance = TinamiComicUrl(parsable_url)
                instance.comic_id = int(comic_id.removesuffix(".php"))
                instance.comic_title = comic_title

            # http://www.tinami.com/today/artworks/t071231_130617.jpg
            # http://www.tinami.com/gallery/img/34_eri_n.jpg
            case ("today" | "gallery"), *_:
                raise UnparsableUrlError(parsable_url)

            case _:
                return None

        return instance
