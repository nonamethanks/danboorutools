from danboorutools.logical.extractors.misskey import MisskeyUrl, MisskeyUserUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class MisskeyIoParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> MisskeyUrl | None:
        match parsable_url.url_parts:
            case username, if username.startswith("@"):
                instance = MisskeyUserUrl(parsable_url)
                instance.username = username.removeprefix("@")
            case _:
                return None

        return instance
