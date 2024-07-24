from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.misskey import MisskeyAssetUrl, MisskeyNoteUrl, MisskeyUrl, MisskeyUserIdUrl, MisskeyUserUrl


class MisskeyIoParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> MisskeyUrl | None:
        match parsable_url.url_parts:
            case username, if username.startswith("@"):
                return MisskeyUserUrl(parsed_url=parsable_url,
                                      username=username.removeprefix("@"))

            case "users", user_id:
                return MisskeyUserIdUrl(parsed_url=parsable_url,
                                        user_id=user_id)

            case "notes", note_id:
                return MisskeyNoteUrl(parsed_url=parsable_url,
                                      note_id=note_id.split("#")[0])

            case _:
                return None


class MisskeyusercontentJp(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> MisskeyUrl | None:
        return MisskeyAssetUrl(parsed_url=parsable_url)
