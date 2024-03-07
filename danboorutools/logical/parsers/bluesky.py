from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.bluesky import BlueskyArtistUrl, BlueskyPostUrl, BskyUrl


class BskyAppParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> BskyUrl | None:
        match parsable_url.url_parts:
            case "profile", username:
                return BlueskyArtistUrl(parsed_url=parsable_url,
                                        username=username)
            case "profile", username, "post", post_id:
                return BlueskyPostUrl(parsed_url=parsable_url,
                                      username=username,
                                      post_id=post_id)
            case _:
                return None


class BskySocialParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> BskyUrl | None:
        match parsable_url.url_parts:
            case [] if parsable_url.subdomain:
                # http://halooge.bsky.social -> https://bsky.app/profile/halooge.bsky.social
                return BlueskyArtistUrl(parsed_url=parsable_url,
                                        username=f"{parsable_url.subdomain}.bsky.social")
            case _:
                return None
