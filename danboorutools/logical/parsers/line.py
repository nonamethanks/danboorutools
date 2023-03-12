from danboorutools.logical.extractors.line import LineArtistUrl, LinePostUrl, LineUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.models.url import UselessUrl


class LineMeParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> LineUrl | UselessUrl | None:
        instance: LineUrl
        match parsable_url.url_parts:
            # https://store.line.me/stickershop/author/344742/en
            case "stickershop", "author", artist_id, *_:
                instance = LineArtistUrl(parsable_url)
                instance.artist_id = int(artist_id)

            # https://store.line.me/stickershop/product/17505/en
            case "stickershop", "product", product_id, *_:
                instance = LinePostUrl(parsable_url)
                instance.product_id = int(product_id)

            # https://line.me/R/ti/p/%40092hdnqj
            case "R", "ti", "p", _:
                return UselessUrl(parsable_url)

            case _:
                return None

        return instance
