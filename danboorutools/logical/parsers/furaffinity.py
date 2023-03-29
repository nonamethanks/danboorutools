from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.furaffinity import (
    FuraffinityArtistImageUrl,
    FuraffinityArtistUrl,
    FuraffinityImageUrl,
    FuraffinityPostUrl,
    FuraffinityUrl,
)


class FuraffinityNetParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FuraffinityUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:

            # https://www.furaffinity.net/view/46802202/
            # https://www.furaffinity.net/full/46821705/
            case ("view" | "full"), post_id, *_:
                return FuraffinityPostUrl(parsed_url=parsable_url,
                                          post_id=int(post_id))

            # https://d.furaffinity.net/art/iwbitu/1650222955/1650222955.iwbitu_yubi.jpg
            case "art", username, _, _:
                return FuraffinityImageUrl(parsed_url=parsable_url,
                                           username=username,
                                           post_id=None)

            # https://www.furaffinity.net/gallery/iwbitu
            # https://www.furaffinity.net/scraps/iwbitu/2/?
            # https://www.furaffinity.net/gallery/iwbitu/folder/133763/Regular-commissions
            # https://www.furaffinity.net/user/lottieloveart/user?user_id=1021820442510802945
            # https://www.furaffinity.net/stats/duskmoor/submissions/
            case ("gallery" | "user" | "favorites" | "scraps" | "journals" | "stats"), username, *_:
                return FuraffinityArtistUrl(parsed_url=parsable_url,
                                            username=username)

            # https://a.furaffinity.net/1550854991/iwbitu.gif
            case _, _ if parsable_url.subdomain == "a":
                return FuraffinityArtistImageUrl(parsed_url=parsable_url)

            # https://t.furaffinity.net/46821705@800-1650222955.jpg
            case filename, if parsable_url.subdomain == "t" and "@" in filename:
                return FuraffinityImageUrl(parsed_url=parsable_url,
                                           post_id=int(filename.split("@")[0]),
                                           username=None)

            case _:
                return None
