from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.profcard import ProfcardUrl


class ProfcardInfoParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ProfcardUrl | None:
        match parsable_url.url_parts:
            case "u", user_id:
                instance = ProfcardUrl(parsable_url)
                instance.user_id = user_id
            case _:
                return None

        return instance
