from danboorutools.logical.extractors.furaffinity import (FuraffinityArtistImageUrl, FuraffinityArtistUrl, FuraffinityImageUrl,
                                                          FuraffinityPostUrl, FuraffinityUrl)
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class FuraffinityNetParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FuraffinityUrl | None:
        instance: FuraffinityUrl

        match parsable_url.url_parts:

            # https://www.furaffinity.net/view/46802202/
            # https://www.furaffinity.net/full/46821705/
            case ("view" | "full"), post_id, *_:
                instance = FuraffinityPostUrl(parsable_url)
                instance.post_id = int(post_id)

            # https://d.furaffinity.net/art/iwbitu/1650222955/1650222955.iwbitu_yubi.jpg
            case "art", username, _, _:
                instance = FuraffinityImageUrl(parsable_url)
                instance.username = username
                instance.post_id = None

            # https://www.furaffinity.net/gallery/iwbitu
            # https://www.furaffinity.net/scraps/iwbitu/2/?
            # https://www.furaffinity.net/gallery/iwbitu/folder/133763/Regular-commissions
            # https://www.furaffinity.net/user/lottieloveart/user?user_id=1021820442510802945
            # https://www.furaffinity.net/stats/duskmoor/submissions/
            case ("gallery" | "user" | "favorites" | "scraps" | "journals" | "stats"), username, *_:
                instance = FuraffinityArtistUrl(parsable_url)
                instance.username = username

            # https://a.furaffinity.net/1550854991/iwbitu.gif
            case _, _ if parsable_url.subdomain == "a":
                instance = FuraffinityArtistImageUrl(parsable_url)

            # https://t.furaffinity.net/46821705@800-1650222955.jpg
            case filename, if parsable_url.subdomain == "t" and "@" in filename:
                instance = FuraffinityImageUrl(parsable_url)
                instance.post_id = int(filename.split("@")[0])
                instance.username = None

            case _:
                return None

        return instance
