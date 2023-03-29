from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.togetter import TogetterArtistUrl, TogetterLiUrl, TogetterPostUrl, TogetterUrl


class TogetterComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> TogetterUrl | None:
        match parsable_url.url_parts:

            # http://togetter.com/id/KRTIT_KRKNS0
            # https://min.togetter.com/id/srm_chi
            case "id", username:
                return TogetterArtistUrl(parsed_url=parsable_url,
                                         username=username)

            # https://togetter.com/li/107987
            case "li", li_id:
                return TogetterLiUrl(parsed_url=parsable_url,
                                     li_id=int(li_id))

            # https://min.togetter.com/yF7scb6
            case post_id, :
                return TogetterPostUrl(parsed_url=parsable_url,
                                       post_id=post_id)

            case _:
                return None
