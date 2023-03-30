from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.potofu import PotofuArtistUrl, PotofuUrl


class PotofuMeParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> PotofuUrl | None:
        match parsable_url.url_parts:
            case user_id, :
                return PotofuArtistUrl(parsed_url=parsable_url,
                                       user_id=user_id)
            case _:
                return None
