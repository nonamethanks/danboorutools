from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.marshmallow_qa import MarshmallowQaUrl


class MarshmallowParser(UrlParser):
    RESERVED_NAMES = ("about", "messages", "broadcasts", "me", "setting", "terms", "help", "users")

    domains = ["marshmallow-qa.com"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> MarshmallowQaUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://marshmallow-qa.com/_ena_ena_?utm_medium=url_text&utm_sou
            case username, if username not in cls.RESERVED_NAMES:
                return MarshmallowQaUrl(parsed_url=parsable_url,
                                        username=username)

            case _:
                return None
