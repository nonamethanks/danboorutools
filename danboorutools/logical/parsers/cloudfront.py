from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.foundation import FoundationImageUrl
from danboorutools.logical.urls.postype import PostypeImageUrl
from danboorutools.models.url import _AssetUrl


class CloudfrontNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> _AssetUrl | None:
        if parsable_url.subdomain == "d2ybmb80bbm9ts":
            match parsable_url.url_parts:
                case _, _, file_hash, _:
                    return FoundationImageUrl(parsed_url=parsable_url,
                                              file_hash=file_hash,
                                              work_id=None,
                                              token_id=None)

                case _:
                    return None
        elif parsable_url.subdomain in ["d2ufj6gm1gtdrc", "d3mcojo3jv0dbr"]:
            match parsable_url.url_parts:
                case _year, _month, _day, _hour, _minute, _file_hash:
                    return PostypeImageUrl(parsed_url=parsable_url)
                case _:
                    return None
        else:
            raise UnparsableUrlError(parsable_url)
