from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import booth as b


class BoothPmParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> b.BoothUrl | None:
        if parsable_url.subdomain not in ("www", "", "s", "s2"):
            return cls._match_username_in_subdomain(parsable_url)
        else:
            return cls._match_everything_else(parsable_url)

    @staticmethod
    def _match_username_in_subdomain(parsable_url: ParsableUrl) -> b.BoothUrl | None:
        match parsable_url.url_parts:

            # https://re-face.booth.pm/items/3435711
            case "items", item_id:
                return b.BoothItemUrl(parsed_url=parsable_url,
                                      item_id=int(item_id),
                                      username=parsable_url.subdomain)

            # https://re-face.booth.pm/item_lists/m4ZTWzb8
            case "item_lists", item_list_id:
                return b.BoothItemListUrl(parsed_url=parsable_url,
                                          item_list_id=item_list_id,
                                          username=parsable_url.subdomain)

            # https://re-face.booth.pm/
            # https://re-face.booth.pm/items
            case _:
                return b.BoothArtistUrl(parsed_url=parsable_url,
                                        user_id=None,
                                        username=parsable_url.subdomain)

    @staticmethod
    def _match_everything_else(parsable_url: ParsableUrl) -> b.BoothUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:

            # https://booth.pm/en/items/2864768
            # https://booth.pm/ja/items/2864768
            case *_, "items", item_id:
                return b.BoothItemUrl(parsed_url=parsable_url,
                                      item_id=int(item_id),
                                      username=None)

            # https://s2.booth.pm/b242a7bd-0747-48c4-891d-9e8552edd5d7/i/3746752/52dbee27-7ad2-4048-9c1d-827eee36625c_base_resized.jpg
            # https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5_base_resized.jpg
            # https://s.booth.pm/1c9bc77f-8ac1-4fa4-94e5-839772ab72cb/i/750997/774dc881-ce6e-45c6-871b-f6c3ca6914d5.png
            case *_, "i", item_id, _:
                return b.BoothImageUrl(parsed_url=parsable_url,
                                       item_id=int(item_id))

            # https://s2.booth.pm/611c108e-1738-4ac6-965a-4d84243d8a3e/386122a4-29b1-4fbc-8887-ac262c12379a.png
            # https://s.booth.pm/548e2f12-31e4-4553-85b0-be309aaa7310/079b78c1-210c-4b8f-b5ba-5d94c5739bab.jpg?1411739802
            case _, _ if parsable_url.subdomain in ["s2", "s"]:
                return b.BoothProfileImageUrl(parsed_url=parsable_url,
                                              user_id=None)

            case "apollo", *_:
                raise UnparsableUrlError(parsable_url)

            case _:
                return None
