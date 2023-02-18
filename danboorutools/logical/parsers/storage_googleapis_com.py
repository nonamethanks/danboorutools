
from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.anifty import AniftyArtistImageUrl, AniftyUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class StorageGoogleapisComParser(UrlParser):
    test_cases = {
        AniftyArtistImageUrl: [
            "https://storage.googleapis.com/anifty-media/creation/0x961d09077b4a9f7a27f6b7ee78cb4c26f0e72c18/20d5ce5b5163a71258e1d0ee152a0347bf40c7da.png",
            "https://storage.googleapis.com/anifty-media/profile/0x961d09077b4a9f7a27f6b7ee78cb4c26f0e72c18/a6d2c366a3e876ddbf04fc269b63124be18af424.png",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> AniftyUrl | None:
        if parsable_url.url_parts[0] == "anifty-media":
            return cls._match_anifty(parsable_url)
        else:
            raise UnparsableUrl(parsable_url)

    @staticmethod
    def _match_anifty(parsable_url: ParsableUrl) -> AniftyUrl | None:
        match parsable_url.url_parts:
            case "anifty-media", ("creation" | "profile") as image_type, artist_hash, _ if artist_hash.startswith("0x"):
                instance = AniftyArtistImageUrl(parsable_url)
                instance.artist_hash = artist_hash
                instance.image_type = image_type
            case _:
                return None

        return instance
