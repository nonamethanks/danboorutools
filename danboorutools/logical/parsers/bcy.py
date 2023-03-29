from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.bcy import BcyArtistUrl, BcyPostUrl, BcyUrl, OldBcyPostUrl


class BcyNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> BcyUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://bcy.net/u/2825982/like
            case "u", user_id, *_:
                return BcyArtistUrl(parsed_url=parsable_url,
                                    user_id=int(user_id))

            # https://bcy.net/item/detail/6576655701886632206
            case "item", "detail", post_id:
                return BcyPostUrl(parsed_url=parsable_url,
                                  post_id=int(post_id))

            # http://bcy.net/illust/detail/9988/801318
            case "illust", "detail", first_id, second_id if first_id.isnumeric() and second_id.isnumeric():
                return OldBcyPostUrl(parsed_url=parsable_url,
                                     first_id=int(first_id),
                                     second_id=int(second_id))

            # https://bcy.net/illust/detail/158436
            # https://bcy.net/coser/detail/89784
            case ("coser" | "illust"), "detail", first_id if first_id.isnumeric():
                return OldBcyPostUrl(parsed_url=parsable_url,
                                     first_id=int(first_id),
                                     second_id=None)

            # http://bcy.net/illust/listhotwork/6821
            case "illust", "listhotwork", _:
                raise UnparsableUrlError(parsable_url)

            # https://bcy.net/cn719869
            case old_id, if old_id.startswith("cn"):  # dead
                raise UnparsableUrlError(parsable_url)

            case _:
                return None
