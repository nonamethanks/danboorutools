from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.misskey import MisskeyUrl, MisskeyUserUrl


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
