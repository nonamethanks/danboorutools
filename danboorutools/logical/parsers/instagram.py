from danboorutools.logical.extractors.instagram import InstagramArtistUrl, InstagramPostUrl, InstagramUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class InstagramComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> InstagramUrl | None:
        instance: InstagramUrl
        match parsable_url.url_parts:

            # https://www.instagram.com/p/CbDW9mVuEnn/
            # https://www.instagram.com/reel/CV7mHEwgbeF/?utm_medium=copy_link
            # https://www.instagram.com/tv/CMjUD1epVWW/
            case ("p" | "reel" | "tv"), post_id:
                instance = InstagramPostUrl(parsable_url)
                instance.post_id = post_id

            # https://www.instagram.com/stories/itomugi/
            case "stories", username, *_:
                instance = InstagramArtistUrl(parsable_url)
                instance.username = username.removeprefix("@")

            # https://www.instagram.com/itomugi/
            # https://www.instagram.com/itomugi/tagged/
            case username, *_:
                instance = InstagramArtistUrl(parsable_url)
                instance.username = username.removeprefix("@")
            case _:
                return None

        return instance
