from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.skeb import SkebAbsolutePostUrl, SkebArtistUrl, SkebImageUrl, SkebPostUrl, SkebUrl


class SkebJpParser(UrlParser):
    RESERVED_USERNAMES = ["works", "users", "about", "terms", "creator", "client", "company"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> SkebUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case username, "works", post_id:
                return SkebPostUrl(parsed_url=parsable_url,
                                   post_id=int(post_id),
                                   username=username.removeprefix("@"))

            case "uploads", "outputs", image_uuid:
                return SkebImageUrl(parsed_url=parsable_url,
                                    image_uuid=image_uuid,
                                    page=None,
                                    post_id=None)

            case "works", post_id:
                return SkebAbsolutePostUrl(parsed_url=parsable_url,
                                           absolute_post_id=int(post_id))

            case username, *_ if username not in cls.RESERVED_USERNAMES:
                return SkebArtistUrl(parsed_url=parsable_url,
                                     username=username.removeprefix("@"))

            case _:
                return None
