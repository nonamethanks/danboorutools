from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.extractors.melonbooks import MelonbooksImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class AkamaizedNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> MelonbooksImageUrl | None:
        if parsable_url.subdomain == "melonbooks":
            return cls._match_melonbooks(parsable_url)
        else:
            raise UnparsableUrlError(parsable_url)

    @staticmethod
    def _match_melonbooks(parsable_url: ParsableUrl) -> MelonbooksImageUrl | None:
        match parsable_url.url_parts:
            # https://melonbooks.akamaized.net/user_data/packages/resize_image.php?width=450&height=450&image=212001389346.jpg&c=1&aa=1
            case "user_data", "packages", "resize_image.php":
                instance = MelonbooksImageUrl(parsable_url)
                instance.filename = parsable_url.query["image"]

            # https://melonbooks.akamaized.net/cplus/user_data/packages/resize_image.php?image=810000212400.jpg\u0026c=0\u0026aa=0
            # https://melonbooks.akamaized.net/fromagee/user_data/packages/resize_image.php?image=216001052635.jpg\u0026c=1\u0026aa=0
            case ("cplus" | "fromagee"), "user_data", "packages", "resize_image.php":
                instance = MelonbooksImageUrl(parsable_url)
                instance.filename = parsable_url.query["image"]

            case _:
                return None

        return instance
