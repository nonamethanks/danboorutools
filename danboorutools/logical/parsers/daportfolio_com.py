from danboorutools.logical.extractors.deviantart import DeviantArtArtistUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class DaportfolioComParser(UrlParser):
    domains = ["daportfolio.com", "artworkfolio.com"]

    test_cases = {
        DeviantArtArtistUrl: [
            "http://nemupanart.daportfolio.com",
            "http://regi-chan.artworkfolio.com",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DeviantArtArtistUrl | None:
        instance = DeviantArtArtistUrl(parsable_url)
        assert parsable_url.subdomain
        instance.username = parsable_url.subdomain
        return instance
