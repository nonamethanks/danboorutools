from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.strategies.stash import StaShUrl


class StaShParser(UrlParser):
    test_cases = {
        StaShUrl: [
            "https://sta.sh/21leo8mz87ue",  # "https://sta.sh/zip/21leo8mz87ue", <- download url
            "https://sta.sh/2uk0v5wabdt",
            "https://sta.sh/0wxs31o7nn2",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> StaShUrl | None:
        match parsable_url.url_parts:
            case (
                ["zip", stash_id] |
                [stash_id]
            ):
                instance = StaShUrl(parsable_url.url)
                instance.stash_id = stash_id
                return instance
            case _:
                return None
