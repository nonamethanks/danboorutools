from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import line as l
from danboorutools.models.url import UnsupportedUrl, Url, UselessUrl


class LineMeParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.subdomain:
            case "store":
                return cls._match_store(parsable_url)
            case "music":
                return cls._match_music(parsable_url)
            case "manga":
                return cls._match_manga(parsable_url)
            case "":
                return cls._match_no_subdomain(parsable_url)
            case _:
                # https://noble.game.line.me/character/img/modern_v3/c10_list.png
                # http://destiny-child-blog.line.me/archives/23074701.html
                if parsable_url.subdomain.endswith("game") or parsable_url.subdomain.endswith("blog"):
                    return UnsupportedUrl(parsable_url)

                return None

    @staticmethod
    def _match_store(parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:
            # https://store.line.me/stickershop/author/344742/en
            case ("stickershop" | "themeshop") as store, "author", artist_id, *_:
                return l.LineArtistUrl(parsed_url=parsable_url,
                                       artist_id=int(artist_id),
                                       store=store)

            # https://store.line.me/stickershop/product/17505/en
            case ("stickershop" | "themeshop")as store, "product", product_id, *_:
                return l.LinePostUrl(parsed_url=parsable_url,
                                     product_id=product_id,
                                     store=store)

            # https://store.line.me/stickershop/detail?packageId=1003926
            case ("stickershop" | "themeshop")as store, "detail":
                return l.LinePostUrl(parsed_url=parsable_url,
                                     product_id=parsable_url.query["packageId"],
                                     store=store)

            # http://store.line.me/stickershop/search/creators/en?q=micca
            # http://store.line.me/stickershop/search/creators/ja?q=Inoki-08
            # http://store.line.me/stickershop/search/creators/?q=Inoki-08
            # http://store.line.me/stickershop/search/en?q=とりのささみ
            # https://store.line.me/search/ja?q=%E5%A4%A7%E5%B3%B6%E6%99%BA%E5%AD%90
            # https://store.line.me/search/en?q=micca
            # https://store.line.me/search/?q=pikaole
            case    ("stickershop", "search", "creators", _) |\
                    ("stickershop", "search", "creators") |\
                    ("stickershop", "search", ("en" | "ja")) |\
                    ("search", _) |\
                    ("search",):
                if list(parsable_url.query.keys()) == ["q"]:
                    return UselessUrl(parsed_url=parsable_url)
                return None

            # http://store.line.me/stickershop/pr
            case "stickershop", "pr":
                return UselessUrl(parsed_url=parsable_url)

            case _:
                return None

    @staticmethod
    def _match_no_subdomain(parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:
            # http://line.me/S/sticker/1363414
            case "S", "sticker", product_id:
                return l.LinePostUrl(parsed_url=parsable_url,
                                     product_id=product_id,
                                     store="stickershop")

            # http://line.me/S/shop/sticker/author/70196
            case "S", "shop", "sticker", "author", artist_id:
                return l.LineArtistUrl(parsed_url=parsable_url,
                                       artist_id=int(artist_id),
                                       store="stickershop")

            # https://line.me/R/ti/p/%40092hdnqj
            # https://line.me/ti/p/YWK_4mveGv
            case *_, "ti", "p", _:
                return UselessUrl(parsed_url=parsable_url)
            case _:
                return None

    @staticmethod
    def _match_manga(parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:
            # http://manga.line.me/indies/author/detail?author_id=761
            case "indies", "author", "detail":
                return l.LineMangaAuthorUrl(parsed_url=parsable_url,
                                            author_id=int(parsable_url.query["author_id"]))

            case _:
                return None

    @staticmethod
    def _match_music(parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:
            # https://music.line.me/webapp/artist/mi00000000167e08b5
            case  "webapp", "artist", artist_id:
                return l.LineMusicArtistUrl(parsed_url=parsable_url,
                                            artist_id=artist_id)

            # https://music.line.me/webapp/album/mb0000000003201a4a
            case "webapp", "album", album_id:
                return l.LineMusicAlbumUrl(parsed_url=parsable_url,
                                           album_id=album_id)

            case _:
                return None
