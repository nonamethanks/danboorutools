from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.vgen import VgenArtistUrl, VgenPostUrl, VgenUrl


class VgenCoParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> VgenUrl | None:
        match parsable_url.url_parts:
            # https://vgen.co/saire/portfolio/showcase/cypher-s-character-illust/3deb91c1-9e45-4242-9c89-53a92047dfea
            case username, "portfolio", "showcase", post_title, post_id:
                return VgenPostUrl(parsed_url=parsable_url,
                                   username=username,
                                   post_title=post_title,
                                   post_id=post_id)

            # https://vgen.co/vennobi
            case username, "portfolio":
                return VgenArtistUrl(parsed_url=parsable_url,
                                     username=username)

            # https://vgen.co/vennobi
            case username, :
                return VgenArtistUrl(parsed_url=parsable_url,
                                     username=username)
            case _:
                return None
