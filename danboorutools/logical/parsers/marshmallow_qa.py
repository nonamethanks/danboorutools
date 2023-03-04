from danboorutools.logical.extractors.marshmallow_qa import MarshmallowQaUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class MarshmallowParser(UrlParser):
    RESERVED_NAMES = ("about", "messages", "broadcasts", "me", "setting", "terms", "help", "users")

    domains = ["marshmallow-qa.com"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> MarshmallowQaUrl | None:
        match parsable_url.url_parts:
            # https://marshmallow-qa.com/_ena_ena_?utm_medium=url_text&utm_sou
            case username, if username not in cls.RESERVED_NAMES:
                instance = MarshmallowQaUrl(parsable_url)
                instance.username = username
            case _:
                return None

        return instance
