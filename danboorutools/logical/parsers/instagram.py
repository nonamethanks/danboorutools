from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.instagram import InstagramArtistUrl, InstagramPostUrl, InstagramUrl


class InstagramComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> InstagramUrl | None:
        match parsable_url.url_parts:

            # https://www.instagram.com/p/CbDW9mVuEnn/
            # https://www.instagram.com/reel/CV7mHEwgbeF/?utm_medium=copy_link
            # https://www.instagram.com/tv/CMjUD1epVWW/
            case ("p" | "reel" | "tv"), post_id:
                return InstagramPostUrl(parsed_url=parsable_url,
                                        post_id=post_id)

            # https://www.instagram.com/stories/itomugi/
            case "stories", username, *_:
                return InstagramArtistUrl(parsed_url=parsable_url,
                                          username=username.removeprefix("@"))

            # https://www.instagram.com/itomugi/
            # https://www.instagram.com/itomugi/tagged/
            case username, *_:
                return InstagramArtistUrl(parsed_url=parsable_url,
                                          username=username.removeprefix("@"))

            case _:
                return None
