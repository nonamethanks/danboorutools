from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.booth import (BoothArtistUrl, BoothImageUrl, BoothItemListUrl, BoothItemUrl, BoothProfileImageUrl,
                                                    BoothUrl)
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class BoothPmParser(UrlParser):
    test_cases = {
        BoothArtistUrl: [
            "https://re-face.booth.pm/",
            "https://re-face.booth.pm/items",
        ],
        BoothImageUrl: [
            "https://s2.booth.pm/b242a7bd-0747-48c4-891d-9e8552edd5d7/i/3746752/52dbee27-7ad2-4048-9c1d-827eee36625c_base_resized.jpg",
            "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5_base_resized.jpg",
            "https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5.png",
        ],
        BoothItemUrl: [
            "https://re-face.booth.pm/items/3435711",

            "https://booth.pm/en/items/2864768",
            "https://booth.pm/ja/items/2864768",
        ],
        BoothItemListUrl: [
            "https://re-face.booth.pm/item_lists/m4ZTWzb8"
        ],
        BoothProfileImageUrl: [
            "https://s2.booth.pm/611c108e-1738-4ac6-965a-4d84243d8a3e/386122a4-29b1-4fbc-8887-ac262c12379a.png",
            "https://s.booth.pm/548e2f12-31e4-4553-85b0-be309aaa7310/079b78c1-210c-4b8f-b5ba-5d94c5739bab.jpg?1411739802",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> BoothUrl | None:
        if parsable_url.subdomain not in ("www", "", "s", "s2"):
            return cls._match_username_in_subdomain(parsable_url)
        else:
            return cls._match_everything_else(parsable_url)

    @staticmethod
    def _match_username_in_subdomain(parsable_url: ParsableUrl) -> BoothUrl | None:
        instance: BoothItemUrl | BoothItemListUrl | BoothArtistUrl
        match parsable_url.url_parts:
            # https://re-face.booth.pm/items/3435711

            # https://re-face.booth.pm/item_lists/m4ZTWzb8

            # https://re-face.booth.pm/
            # https://re-face.booth.pm/items
            case "items", item_id:
                instance = BoothItemUrl(parsable_url)
                instance.item_id = int(item_id)
            case "item_lists", item_list_id:
                instance = BoothItemListUrl(parsable_url)
                instance.item_list_id = item_list_id
            case _:
                instance = BoothArtistUrl(parsable_url)
                instance.user_id = None

        instance.username = parsable_url.subdomain
        return instance

    @staticmethod
    def _match_everything_else(parsable_url: ParsableUrl) -> BoothUrl | None:
        instance: BoothUrl
        match parsable_url.url_parts:
            # https://booth.pm/en/items/2864768
            # https://booth.pm/ja/items/2864768
            case *_, "items", item_id:
                instance = BoothItemUrl(parsable_url)
                instance.item_id = int(item_id)
                instance.username = None
            # https://s2.booth.pm/b242a7bd-0747-48c4-891d-9e8552edd5d7/i/3746752/52dbee27-7ad2-4048-9c1d-827eee36625c_base_resized.jpg
            # https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5_base_resized.jpg
            # https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5.png
            case *_, "i", item_id, _:
                instance = BoothImageUrl(parsable_url)
                instance.item_id = int(item_id)

            # https://s2.booth.pm/611c108e-1738-4ac6-965a-4d84243d8a3e/386122a4-29b1-4fbc-8887-ac262c12379a.png
            # https://s.booth.pm/548e2f12-31e4-4553-85b0-be309aaa7310/079b78c1-210c-4b8f-b5ba-5d94c5739bab.jpg?1411739802
            case _, _ if parsable_url.subdomain in ["s2", "s"]:
                instance = BoothProfileImageUrl(parsable_url)
                instance.user_id = None

            case "apollo", *_:
                raise UnparsableUrl(parsable_url)
            case _:
                return None

        return instance
