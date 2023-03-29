from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.deviantart import DeviantArtImageUrl


class KnownHosts:
    DEVIANTART = ("images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com", "wixmp-ed30a86b8c4ca887773594c2.wixmp.com")


class WixmpComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DeviantArtImageUrl | None:
        if parsable_url.hostname in KnownHosts.DEVIANTART:
            username, deviation_id, title = DeviantArtImageUrl.parse_filename(parsable_url.filename)
            return DeviantArtImageUrl(parsed_url=parsable_url,
                                      username=username,
                                      deviation_id=deviation_id,
                                      title=title)
        elif parsable_url.raw_url.startswith("https://api-da.wixmp.com/_api/download/file"):
            raise UnparsableUrlError(parsable_url)

        return None
