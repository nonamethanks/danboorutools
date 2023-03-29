from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.anifty import AniftyArtistUrl, AniftyPostUrl, AniftyTokenUrl, AniftyUrl


class AniftyJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AniftyUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case *_, "creations", post_id:
                return AniftyPostUrl(parsed_url=parsable_url,
                                     post_id=int(post_id))

            case *_, username if username.startswith("@"):
                return AniftyArtistUrl(parsed_url=parsable_url,
                                       username=username.removeprefix("@"))

            case *_, "tokens", token_id:
                return AniftyTokenUrl(parsed_url=parsable_url,
                                      token_id=int(token_id))

            case _:
                return None
