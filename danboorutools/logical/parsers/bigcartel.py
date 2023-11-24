from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.bigcartel import BigcartelArtistUrl, BigcartelImageUrl, BigcartelPostUrl, BigcartelUrl
from danboorutools.models.url import UselessUrl


class BigcartelComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> BigcartelUrl | UselessUrl | None:
        if parsable_url.subdomain in ("www", ""):
            return UselessUrl(parsable_url)

        if parsable_url.subdomain in ("images", "assets"):
            return BigcartelImageUrl(parsable_url)

        match parsable_url.url_parts:
            case "product", post_id:
                return BigcartelPostUrl(parsed_url=parsable_url,
                                        username=parsable_url.subdomain,
                                        post_id=post_id)

            case _:
                return BigcartelArtistUrl(parsed_url=parsable_url,
                                          username=parsable_url.subdomain)
