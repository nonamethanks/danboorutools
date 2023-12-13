from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.misskey import MisskeyUrl, MisskeyUserIdUrl, MisskeyUserUrl


class MisskeyIoParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> MisskeyUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case username, if username.startswith("@"):
                return MisskeyUserUrl(parsed_url=parsable_url,
                                      username=username.removeprefix("@"))

            case "users", user_id:
                return MisskeyUserIdUrl(parsed_url=parsable_url,
                                        user_id=user_id)

            case _:
                return None
