from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.profcard import ProfcardUrl


class ProfcardInfoParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ProfcardUrl | None:
        match parsable_url.url_parts:
            case "u", user_id:
                return ProfcardUrl(parsed_url=parsable_url,
                                   user_id=user_id)

            case _:
                return None
