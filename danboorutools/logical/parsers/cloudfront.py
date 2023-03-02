from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.foundation import FoundationImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class CloudfrontNetParser(UrlParser):
    test_cases = {
        FoundationImageUrl: [
            "https://d2ybmb80bbm9ts.cloudfront.net/zd/BD/QmXiCEoBLcpfvpEwAEanLXe3Tjr5ykYJFzCVfpzDDQzdBD/nft_q4.mp4",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FoundationImageUrl | None:
        if parsable_url.subdomain == "d2ybmb80bbm9ts":
            match parsable_url.url_parts:
                case _, _, file_hash, _:
                    instance = FoundationImageUrl(parsable_url)
                    instance.file_hash = file_hash
                    instance.work_id = None
                    instance.token_id = None
                case _:
                    return None

            return instance
        else:
            raise UnparsableUrl(parsable_url)
