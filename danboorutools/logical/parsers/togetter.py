from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.togetter import TogetterArtistUrl, TogetterLiUrl, TogetterPostUrl, TogetterUrl


class TogetterComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> TogetterUrl | None:
        instance: TogetterUrl

        match parsable_url.url_parts:

            # http://togetter.com/id/KRTIT_KRKNS0
            # https://min.togetter.com/id/srm_chi
            case "id", username:
                instance = TogetterArtistUrl(parsable_url)
                instance.username = username

            # https://togetter.com/li/107987
            case "li", li_id:
                instance = TogetterLiUrl(parsable_url)
                instance.li_id = int(li_id)

            # https://min.togetter.com/yF7scb6
            case post_id, :
                instance = TogetterPostUrl(parsable_url)
                instance.post_id = post_id

            case _:
                return None

        return instance
