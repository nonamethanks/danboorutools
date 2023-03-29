from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.line import LineArtistUrl, LineMangaAuthorUrl, LinePostUrl, LineUrl
from danboorutools.models.url import UselessUrl


class LineMeParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> LineUrl | UselessUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://store.line.me/stickershop/author/344742/en
            case ("stickershop" | "themeshop") as store, "author", artist_id, *_:
                return LineArtistUrl(parsed_url=parsable_url,
                                     artist_id=int(artist_id),
                                     store=store)

            # https://store.line.me/stickershop/product/17505/en
            case ("stickershop" | "themeshop")as store, "product", product_id, *_:
                return LinePostUrl(parsed_url=parsable_url,
                                   product_id=product_id,
                                   store=store)

            # https://store.line.me/stickershop/detail?packageId=1003926
            case ("stickershop" | "themeshop")as store, "detail":
                return LinePostUrl(parsed_url=parsable_url,
                                   product_id=parsable_url.query["packageId"],
                                   store=store)

            # http://line.me/S/sticker/1363414
            case "S", "sticker", product_id:
                return LinePostUrl(parsed_url=parsable_url,
                                   product_id=product_id,
                                   store="stickershop")

            # http://line.me/S/shop/sticker/author/70196
            case "S", "shop", "sticker", "author", artist_id:
                return LineArtistUrl(parsed_url=parsable_url,
                                     artist_id=int(artist_id),
                                     store="stickershop")

            # http://manga.line.me/indies/author/detail?author_id=761
            case "indies", "author", "detail":
                return LineMangaAuthorUrl(parsed_url=parsable_url,
                                          author_id=int(parsable_url.query["author_id"]))

            # https://noble.game.line.me/character/img/modern_v3/c10_list.png
            # http://destiny-child-blog.line.me/archives/23074701.html
            case _ if parsable_url.subdomain.endswith("game") or parsable_url.subdomain.endswith("blog"):
                raise UnparsableUrlError(parsable_url)

            # http://store.line.me/stickershop/search/creators/en?q=micca
            # http://store.line.me/stickershop/search/creators/ja?q=Inoki-08
            # http://store.line.me/stickershop/search/creators/?q=Inoki-08
            # http://store.line.me/stickershop/search/en?q=とりのささみ
            # https://store.line.me/search/ja?q=%E5%A4%A7%E5%B3%B6%E6%99%BA%E5%AD%90
            # https://store.line.me/search/en?q=micca
            case    ("stickershop", "search", "creators", _) |\
                    ("stickershop", "search", "creators") |\
                    ("stickershop", "search", "en") |\
                    ("search", _):
                if list(parsable_url.query.keys()) == ["q"]:
                    return UselessUrl(parsed_url=parsable_url)
                return None

            # https://line.me/R/ti/p/%40092hdnqj
            # https://line.me/ti/p/YWK_4mveGv
            case *_, "ti", "p", _:
                return UselessUrl(parsed_url=parsable_url)

            # http://store.line.me/stickershop/pr
            case "stickershop", "pr":
                return UselessUrl(parsed_url=parsable_url)

            case _:
                return None
