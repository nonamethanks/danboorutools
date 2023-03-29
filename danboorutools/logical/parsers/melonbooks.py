from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import melonbooks as mb


class MelonbooksCoJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> mb.MelonbooksUrl | None:  # type: ignore[return]
        if parsable_url.subdomain in ("shop", ):
            raise UnparsableUrlError(parsable_url)

        match parsable_url.url_parts:
            # https://www.melonbooks.co.jp/detail/detail.php?product_id=1484137&adult_view=1
            # https://www.melonbooks.co.jp/fromagee/detail/detail.php?product_id=1033195 # l'omelette du fromagee
            case *_, "detail", "detail.php":
                return mb.MelonbooksProductUrl(parsed_url=parsable_url,
                                               product_id=int(parsable_url.query["product_id"]))

            # https://www.melonbooks.co.jp/circle/index.php?circle_id=107578
            # https://www.melonbooks.co.jp/circle/index.php?circle_id=107578#
            case *_, "circle", "index.php":
                return mb.MelonbooksCircleUrl(parsed_url=parsable_url,
                                              circle_id=int(parsable_url.query["circle_id"].split("#")[0]))

            # https://www.melonbooks.co.jp/circle/?circle_id=30826
            # https://www.melonbooks.co.jp/fromagee/circle/?circle_id=32501
            case *_, "circle", :
                return mb.MelonbooksCircleUrl(parsed_url=parsable_url,
                                              circle_id=int(parsable_url.query["circle_id"]))

            # https://www.melonbooks.co.jp/corner/detail.php?corner_id=769
            # https://www.melonbooks.co.jp/corner/detail.php?corner_id=769#gnav
            case "corner", "detail.php":
                return mb.MelonbooksCornerUrl(parsed_url=parsable_url,
                                              corner_id=int(parsable_url.query["corner_id"].split("#")[0]))

            # https://www.melonbooks.co.jp/special/a/6/pb/sp/komeshiro_illust30_up.jpg
            # https://www.melonbooks.co.jp/special/b/0/fair_dojin/20181229_touhousuiseisou2/images/itemimg5/img6_1.png
            case "special", dir1, dir2, *_ if len(dir1) == 1 and len(dir2) == 1:
                return mb.MelonbooksImageUrl(parsed_url=parsable_url,
                                             filename=None)

            # https://www.melonbooks.co.jp/resize_image.php?image=212001389346.jpg
            case "resize_image.php", :
                return mb.MelonbooksImageUrl(parsed_url=parsable_url,
                                             filename=parsable_url.query["image"])

            # https://www.melonbooks.co.jp/search/search.php?name=%E6%8A%B9%E8%8C%B6%E3%81%AD%E3%81%98&text_type=author
            case *_, "search", "search.php" if parsable_url.query.get("text_type") == "author":
                return mb.MelonbooksAuthorUrl(parsed_url=parsable_url,
                                              artist_name=parsable_url.query["name"])

            # https://www.melonbooks.co.jp/search/search.php?name=%E6%98%8E%E5%9C%B0%E9%9B%AB
            case *_, "search", "search.php" if "name" in parsable_url.query and len(parsable_url.query) == 1:
                return mb.MelonbooksAuthorUrl(parsed_url=parsable_url,
                                              artist_name=parsable_url.query["name"])

            # http://www.melonbooks.co.jp/blogs/log/image/img08090005_1.jpg
            case "blogs", "log", "image", *_:
                return mb.MelonbooksImageUrl(parsed_url=parsable_url,
                                             filename=None)

            case _:
                return None
