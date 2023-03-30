from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.potofu import PotofuArtistUrl, PotofuUrl


class PotofuMeParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PotofuUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case user_id, if user_id.isnumeric():
                return PotofuArtistUrl(parsed_url=parsable_url,
                                       user_id=int(user_id))
            case _:
                return None
