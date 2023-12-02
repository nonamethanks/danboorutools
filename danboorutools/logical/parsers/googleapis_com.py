from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.anifty import AniftyArtistImageUrl, AniftyImageUrl, AniftyUrl


class GoogleapisComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AniftyUrl | None:
        if parsable_url.url_parts[0] == "anifty-media":
            return cls._match_anifty(parsable_url)
        else:
            raise UnparsableUrlError(parsable_url)

    @staticmethod
    def _match_anifty(parsable_url: ParsableUrl) -> AniftyUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case "anifty-media", ("creation" | "profile") as image_type, artist_hash, filename if artist_hash.startswith("0x"):
                if image_type == "profile":
                    return AniftyArtistImageUrl(parsed_url=parsable_url,
                                                artist_hash=artist_hash,
                                                filename=filename)

                else:
                    return AniftyImageUrl(parsed_url=parsable_url,
                                          artist_hash=artist_hash,
                                          filename=filename)

            case _:
                return None
