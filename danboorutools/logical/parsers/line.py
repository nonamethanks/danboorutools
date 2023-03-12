from danboorutools.logical.extractors.line import LineArtistUrl, LineMangaAuthorUrl, LinePostUrl, LineUrl
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

            # https://store.line.me/stickershop/detail?packageId=1003926
            case "stickershop", "detail":
                instance = LinePostUrl(parsable_url)
                instance.product_id = int(parsable_url.query["packageId"])

            # http://line.me/S/sticker/1363414
            case "S", "sticker", product_id:
                instance = LinePostUrl(parsable_url)
                instance.product_id = int(product_id)

            # http://line.me/S/shop/sticker/author/70196
            case "S", "shop", "sticker", "author", artist_id:
                instance = LineArtistUrl(parsable_url)
                instance.artist_id = int(artist_id)

            # http://manga.line.me/indies/author/detail?author_id=761
            case "indies", "author", "detail":
                instance = LineMangaAuthorUrl(parsable_url)
                instance.author_id = int(parsable_url.query["author_id"])

            # http://store.line.me/stickershop/search/creators/en?q=micca
            # http://store.line.me/stickershop/search/creators/ja?q=Inoki-08
            # http://store.line.me/stickershop/search/creators/?q=Inoki-08
            # http://store.line.me/stickershop/search/en?q=とりのささみ
            # https://store.line.me/search/en?q=micca
            case    ("stickershop", "search", "creators", _) |\
                    ("stickershop", "search", "creators") |\
                    ("stickershop", "search", "en") |\
                    ("search", "en"):
                if list(parsable_url.query.keys()) == ["q"]:
                    return UselessUrl(parsable_url)
                return None

            # https://line.me/R/ti/p/%40092hdnqj
            # https://line.me/ti/p/YWK_4mveGv
            case *_, "ti", "p", _:
                return UselessUrl(parsable_url)

            # http://store.line.me/stickershop/pr
            case "stickershop", "pr":
                return UselessUrl(parsable_url)

            case _:
                return None

        return instance
