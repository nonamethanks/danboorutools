from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.foundation import FoundationImageUrl


class CloudfrontNetParser(UrlParser):
    test_cases = {
        FoundationImageUrl: [
            "https://d2ybmb80bbm9ts.cloudfront.net/zd/BD/QmXiCEoBLcpfvpEwAEanLXe3Tjr5ykYJFzCVfpzDDQzdBD/nft_q4.mp4",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FoundationImageUrl | None:
        if parsable_url.subdomain == "d2ybmb80bbm9ts":
            match parsable_url.url_parts:
                case _, _, file_hash, _:
                    return FoundationImageUrl(parsed_url=parsable_url,
                                              file_hash=file_hash,
                                              work_id=None,
                                              token_id=None)

                case _:
                    return None
        else:
            raise UnparsableUrlError(parsable_url)
