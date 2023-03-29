from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.gumroad import GumroadArtistUrl, GumroadImageUrl, GumroadPostNoArtist, GumroadPostUrl, GumroadUrl


class GumroadComParser(UrlParser):
    reserved_names = ["gumroad", "help", "features", "pricing", "university", "discover", "blog", "login", "signup", "l"]
    reserved_subdomains = ["", "www", "gumroad", "app"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> GumroadUrl | None:
        # https://public-files.gumroad.com/zly28g1k8xyhvrzcm0ngs596jb1d
        # https://public-files.gumroad.com/variants/nyciujfjsdcfh6vj9j5om56lve7z/e82ce07851bf15f5ab0ebde47958bb042197dbcdcae02aa122ef3f5b41e97c02
        # https://static-2.gumroad.com/res/gumroad/6148433509922/asset_previews/7e296db4cc949bb42eb2ac73b6b92f42/retina/samus_dada_normal.jpg
        if parsable_url.subdomain == "public-files" or parsable_url.subdomain.startswith("static-"):
            return GumroadImageUrl(parsable_url)
        elif parsable_url.subdomain not in cls.reserved_subdomains:
            return cls._match_username_in_subdomain(parsable_url)
        elif parsable_url.subdomain in ["", "www", "app"]:
            return cls._match_no_subdomain(parsable_url)
        else:
            return None

    @staticmethod
    def _match_username_in_subdomain(parsable_url: ParsableUrl) -> GumroadUrl | None:
        instance: GumroadUrl
        match parsable_url.url_parts:
            # https://fishsyrup.gumroad.com/l/WkjEj
            # https://fishsyrup.gumroad.com/l/WkjEj/ibdkpxx
            case "l", post_id, *_rest:
                instance = GumroadPostUrl(parsable_url)
                instance.post_id = post_id
                instance.username = parsable_url.subdomain

            # https://roborobocap.gumroad.com
            case []:
                instance = GumroadArtistUrl(parsable_url)
                instance.username = parsable_url.subdomain
            case _:
                return None

        return instance

    @classmethod
    def _match_no_subdomain(cls, parsable_url: ParsableUrl) -> GumroadUrl | None:
        instance: GumroadUrl
        match parsable_url.url_parts:

            case username, "follow":
                instance = GumroadArtistUrl(parsable_url)
                instance.username = username

            # https://app.gumroad.com/roborobocap
            case username, if username not in cls.reserved_names:
                instance = GumroadArtistUrl(parsable_url)
                instance.username = username

            # https://gumroad.com/l/WkjEj/ibdkpxx
            # http://app.gumroad.com/l/uSukO/
            case "l", post_id, *_rest:
                instance = GumroadPostNoArtist(parsable_url)
                instance.post_id = post_id
            case _:
                return None

        return instance
