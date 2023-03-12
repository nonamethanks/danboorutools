from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.bcy import BcyArtistUrl, BcyPostUrl, BcyUrl, OldBcyPostUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class BcyNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> BcyUrl | None:
        instance: BcyUrl

        match parsable_url.url_parts:
            case "u", user_id, *_:
                instance = BcyArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            case "item", "detail", post_id:
                instance = BcyPostUrl(parsable_url)
                instance.post_id = int(post_id)

            case "illust", "detail", first_id, second_id if first_id.isnumeric() and second_id.isnumeric():
                instance = OldBcyPostUrl(parsable_url)
                instance.first_id = int(first_id)
                instance.second_id = int(second_id)

            case "illust", "listhotwork", _:  # http://bcy.net/illust/listhotwork/6821
                raise UnparsableUrl(parsable_url)

            case old_id, if old_id.startswith("cn"):  # dead
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance
