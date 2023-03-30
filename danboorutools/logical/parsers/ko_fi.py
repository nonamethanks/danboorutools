from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.ko_fi import KoFiArtistUrl, KoFiImageUrl, KoFiPostUrl, KofiShopPostUrl, KoFiUrl
from danboorutools.models.url import UselessUrl


class KoFiParser(UrlParser):
    domains = ["ko-fi.com"]

    reserved_usernames = ("manage", "messages", "my-supporters", "settings", "explore", "memberships",
                          "shop", "Discord", "streamalerts", "account", "discount", "access", "cdn", "s")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> KoFiUrl | UselessUrl | None:  # type: ignore[return]
        if parsable_url.subdomain == "help":
            return UselessUrl(parsable_url)

        if parsable_url.subdomain in ["cdn", "storage"]:
            return KoFiImageUrl(parsable_url)

        match parsable_url.url_parts:
            # https://ko-fi.com/i/IW7W1JB2Y2
            case "i", post_id:
                return KoFiPostUrl(parsed_url=parsable_url,
                                   post_id=post_id)

            # https://ko-fi.com/annluvazzel?viewimage=IE1E1FSB3S#galleryItemView
            case username, if "viewimage" in parsable_url.query:
                return KoFiPostUrl(parsed_url=parsable_url,
                                   post_id=parsable_url.query["viewimage"].split("#")[0])

            # https://ko-fi.com/chezforshire/commissions
            # https://ko-fi.com/chezforshire/gallery
            case username, slug if not parsable_url.query and slug.split("#")[0] in ("commissions", "gallery", "shop", "posts"):
                return KoFiArtistUrl(parsed_url=parsable_url,
                                     username=username)

            # https://ko-fi.com/chezforshire
            case username, if username not in cls.reserved_usernames and not parsable_url.query:
                return KoFiArtistUrl(parsed_url=parsable_url,
                                     username=username)

            # https://ko-fi.com/s/587d9729ac
            case "s", shop_id:
                return KofiShopPostUrl(parsed_url=parsable_url,
                                       shop_id=shop_id)
            case _:
                return None
