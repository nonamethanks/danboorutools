from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.myportfolio import MyportfolioArtistUrl, MyportfolioImageUrl, MyportfolioUrl
from danboorutools.models.url import UnsupportedUrl, UselessUrl


class MyportfolioComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> MyportfolioUrl | UselessUrl | None:
        if parsable_url.subdomain in ["www", ""]:
            return UselessUrl(parsed_url=parsable_url)
        if parsable_url.subdomain == "cdn" or "-cdn-" in parsable_url.subdomain:
            return MyportfolioImageUrl(parsed_url=parsable_url)

        match parsable_url.url_parts:
            case []:
                return MyportfolioArtistUrl(parsed_url=parsable_url,
                                            username=parsable_url.subdomain)
            case ("profile" | "work" | "art" | "home"), :
                return MyportfolioArtistUrl(parsed_url=parsable_url,
                                            username=parsable_url.subdomain)

            case _, :
                return UnsupportedUrl(parsed_url=parsable_url)
            case _:
                return None
