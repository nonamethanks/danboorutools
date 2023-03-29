from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.linktree import LinktreeUrl


class LinktrEeParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> LinktreeUrl | None:
        match parsable_url.url_parts:
            # https://linktr.ee/tyanka6
            case username, :
                return LinktreeUrl(parsed_url=parsable_url,
                                   username=username)

            case _:
                return None
