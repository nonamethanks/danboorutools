from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.strategies.deviantart import DeviantArtArtistUrl


class DaportfolioComParser(UrlParser):
    test_cases = {
        DeviantArtArtistUrl: ["http://nemupanart.daportfolio.com"]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DeviantArtArtistUrl | None:
        instance = DeviantArtArtistUrl(parsable_url.url)
        assert parsable_url.subdomain
        instance.username = parsable_url.subdomain
        return instance
