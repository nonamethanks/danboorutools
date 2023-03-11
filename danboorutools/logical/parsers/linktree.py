from danboorutools.logical.extractors.linktree import LinktreeUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class LinktrEeParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> LinktreeUrl | None:
        match parsable_url.url_parts:
            # https://linktr.ee/tyanka6
            case username, :
                instance = LinktreeUrl(parsable_url)
                instance.username = username
            case _:
                return None

        return instance
