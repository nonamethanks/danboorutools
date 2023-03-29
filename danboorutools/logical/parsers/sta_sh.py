from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.stash import StaShUrl


class StaShParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> StaShUrl | None:
        match parsable_url.url_parts:
            case (
                ["zip", stash_id] |
                [stash_id]
            ):
                return StaShUrl(parsed_url=parsable_url,
                                stash_id=stash_id)
            case _:
                return None
