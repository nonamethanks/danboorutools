from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors import melonbooks as mb
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class MelonbooksCoJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> mb.MelonbooksUrl | None:
        instance: mb.MelonbooksUrl

        if parsable_url.subdomain in ("shop", ):
            raise UnparsableUrl(parsable_url)

        match parsable_url.url_parts:
            # https://www.melonbooks.co.jp/detail/detail.php?product_id=1484137&adult_view=1
            # https://www.melonbooks.co.jp/fromagee/detail/detail.php?product_id=1033195 # l'omelette du fromagee
            case *_, "detail", "detail.php":
                instance = mb.MelonbooksProductUrl(parsable_url)
                instance.product_id = int(parsable_url.query["product_id"])

            # https://www.melonbooks.co.jp/circle/index.php?circle_id=107578
            # https://www.melonbooks.co.jp/circle/index.php?circle_id=107578#
            case *_, "circle", "index.php":
                instance = mb.MelonbooksCircleUrl(parsable_url)
                instance.circle_id = int(parsable_url.query["circle_id"].split("#")[0])

            # https://www.melonbooks.co.jp/circle/?circle_id=30826
            # https://www.melonbooks.co.jp/fromagee/circle/?circle_id=32501
            case *_, "circle", :
                instance = mb.MelonbooksCircleUrl(parsable_url)
                instance.circle_id = int(parsable_url.query["circle_id"])

            # https://www.melonbooks.co.jp/corner/detail.php?corner_id=769
            # https://www.melonbooks.co.jp/corner/detail.php?corner_id=769#gnav
            case "corner", "detail.php":
                instance = mb.MelonbooksCornerUrl(parsable_url)
                instance.corner_id = int(parsable_url.query["corner_id"].split("#")[0])

            # https://www.melonbooks.co.jp/special/a/6/pb/sp/komeshiro_illust30_up.jpg
            # https://www.melonbooks.co.jp/special/b/0/fair_dojin/20181229_touhousuiseisou2/images/itemimg5/img6_1.png
            case "special", dir1, dir2, *_ if len(dir1) == 1 and len(dir2) == 1:
                instance = mb.MelonbooksImageUrl(parsable_url)
                instance.filename = None

            # https://www.melonbooks.co.jp/resize_image.php?image=212001389346.jpg
            case "resize_image.php", :
                instance = mb.MelonbooksImageUrl(parsable_url)
                instance.filename = parsable_url.query["image"]

            # https://www.melonbooks.co.jp/search/search.php?name=%E6%8A%B9%E8%8C%B6%E3%81%AD%E3%81%98&text_type=author
            case *_, "search", "search.php" if parsable_url.query.get("text_type") == "author":
                instance = mb.MelonbooksAuthorUrl(parsable_url)
                instance.artist_name = parsable_url.query["name"]

            # https://www.melonbooks.co.jp/search/search.php?name=%E6%98%8E%E5%9C%B0%E9%9B%AB
            case *_, "search", "search.php" if "name" in parsable_url.query and len(parsable_url.query) == 1:
                instance = mb.MelonbooksAuthorUrl(parsable_url)
                instance.artist_name = parsable_url.query["name"]

            # http://www.melonbooks.co.jp/blogs/log/image/img08090005_1.jpg
            case "blogs", "log", "image", *_:
                instance = mb.MelonbooksImageUrl(parsable_url)
                instance.filename = None

            case _:
                return None

        return instance
