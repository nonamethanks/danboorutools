from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.extractors.toranoana import (
    ToranoanaArtistUrl,
    ToranoanaCircleUrl,
    ToranoanaDojinSeriesUrl,
    ToranoanaImageUrl,
    ToranoanaItemUrl,
    ToranoanaOldAuthorUrl,
    ToranoanaOldCircleUrl,
    ToranoanaUrl,
    ToranoanaWebcomicPageUrl,
)
from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.models.url import UselessUrl


class ToranoanaJpParser(UrlParser):
    subdirs = ("tora", "tora_r", "tora_rd", "joshi", "joshi_r")
    subdir_map = {
        "mailorder": "tora_r",
        "bl": "joshi_r",
    }

    book_types = ("cot", "cit", "ebk")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ToranoanaUrl | UselessUrl | None:
        if not parsable_url.url_parts:
            return UselessUrl(parsable_url)
        # http://img.toranoana.jp/popup_img/04/0030/13/81/040030138104-3p.jpg
        if parsable_url.subdomain == "img":  # not normalizable
            raise UnparsableUrlError(parsable_url)

        # https://news.toranoana.jp/178996
        if parsable_url.subdomain == "news":  # not worth it
            raise UnparsableUrlError(parsable_url)

        if parsable_url.subdomain == "ecdnimg":
            return cls._match_img(parsable_url)
        else:
            return cls._match_everything_else(parsable_url)

    @staticmethod
    def _match_img(parsable_url: ParsableUrl) -> ToranoanaUrl | None:
        match parsable_url.url_parts:
            # https://ecdnimg.toranoana.jp/ec/img/04/0030/80/38/040030803886-1p.jpg
            # https://ecdnimg.toranoana.jp/ec/img/04/0030/80/38/040030803886-1p_thumb.jpg
            case "ec", "img", _, _, _, _, _:
                instance = ToranoanaImageUrl(parsable_url)
                [instance.post_id, page] = parsable_url.stem.removesuffix("_thumb").split("-")
                instance.page = int(page.removesuffix("p"))

            case _:
                return None

        return instance

    @classmethod
    def _match_everything_else(cls, parsable_url: ParsableUrl) -> ToranoanaUrl | UselessUrl | None:
        instance: ToranoanaUrl
        match parsable_url.url_parts:
            # https://ec.toranoana.jp/tora_r/ec/item/040030865238/
            case subdir1, ("ec" | "digi") as subdir2, "item", item_id:
                instance = ToranoanaItemUrl(parsable_url)
                subdir1 = subdir1 if subdir1 in cls.subdirs else cls.subdir_map[subdir1]
                instance.subdirs = f"{subdir1}/ec"
                instance.item_id = item_id
                instance.subsite = parsable_url.subdomain if parsable_url.subdomain != "www" else "ec"

            # https://ec.toranoana.jp/joshi_r/ec/app/catalog/list?actorKindId=作家★☆★ACTR000002008202
            case subdir1,  ("ec" | "digi") as subdir2, "app", "catalog", "list":
                instance = ToranoanaArtistUrl(parsable_url)
                subdir1 = subdir1 if subdir1 in cls.subdirs else cls.subdir_map[subdir1]
                instance.subdirs = f"{subdir1}/{subdir2}"
                instance.subsite = parsable_url.subdomain
                if artist_name := parsable_url.query.get("actorKindId"):
                    instance.artist_type = "actorKindId"
                    instance.artist_name = artist_name
                elif artist_name := parsable_url.query.get("searchActorName"):
                    instance.artist_type = "searchActorName"
                    instance.artist_name = artist_name
                else:
                    return None

            # http://www.toranoana.jp/mailorder/article/04/0030/82/37/040030823758.html
            # http://www.toranoana.jp/bl/article/04/0030/51/17/040030511769.html
            case subdir, "article", _, _, _, _, item_id:
                instance = ToranoanaItemUrl(parsable_url)
                instance.item_id = item_id.removesuffix(".html")
                subdir = subdir if subdir in cls.subdirs else cls.subdir_map[subdir]
                instance.subdirs = f"{subdir}/ec"
                instance.subsite = parsable_url.subdomain if parsable_url.subdomain != "www" else "ec"

            # https://ec.toranoana.jp/tora_r/ec/cot/circle/2UPA346P8473d46Pd687/all/
            # https://ecs.toranoana.jp/tora/ec/cot/circle/LUPAdB6Q8U75d06pd687/all/
            # https://ec.toranoana.jp/joshi_r/ec/cot/circle/2UPA1C6P8X7LdE6Rd687/all/
            case subdir1, ("ec" | "digi") as subdir2, ("cot" | "cit" | "ebk") as subdir3, "circle", circle_id, "all":
                instance = ToranoanaCircleUrl(parsable_url)
                instance.circle_id = circle_id
                subdir1 = subdir1 if subdir1 in cls.subdirs else cls.subdir_map[subdir1]
                instance.subdirs = f"{subdir1}/{subdir2}/{subdir3}"
                instance.subsite = parsable_url.subdomain

            # https://www.toranoana.jp/webcomic/holic/esora/webcomic/4koma/karaage/0001/02.html
            case "webcomic", "holic", publisher, "webcomic", "4koma", webcomic_title, webcomic_entry, _filename:
                instance = ToranoanaWebcomicPageUrl(parsable_url)
                instance.publisher = publisher
                instance.webcomic_title = webcomic_title
                instance.webcomic_entry = webcomic_entry

            # http://www.toranoana.jp/webcomic/holic/esora/webcomic/hebe/0003/10.jpg
            case "webcomic", "holic", publisher, "webcomic", webcomic_title, webcomic_entry, _filename:
                instance = ToranoanaWebcomicPageUrl(parsable_url)
                instance.publisher = publisher
                instance.webcomic_title = webcomic_title
                instance.webcomic_entry = webcomic_entry

            # http://www.toranoana.jp/info/dojin/120810_oyakokodon/
            case "info", "dojin", dojin_slug:
                instance = ToranoanaDojinSeriesUrl(parsable_url)
                instance.dojin_slug = dojin_slug

            # http://www.toranoana.jp/mailorder/cot/author/95/3675_01.html
            # http://www.toranoana.jp/bl/cot/author/14/a4a8a4b0_01.html
            case ("bl" | "mailorder"), ("cot" | "cit" | "ebk"), "author", _, _:
                instance = ToranoanaOldAuthorUrl(parsable_url)

            # http://www.toranoana.jp/mailorder/cot/circle/81/02/5730303330323831/b4c5b2c6a5c9a5eda5c3a5d7_01.html
            # http://www.toranoana.jp/mailorder/cit/circle/79/32/5730383533323739/b5fec5d4b8b8c1dbb7e0c3c4_01.html
            # http://www.toranoana.jp/mailorder/ebk/circle/32/93/5730353439333332/cbf5c3e3a5c9a1bca5eb_01.html
            # http://www.toranoana.jp/bl/cot/circle/18/63/5730303836333138/416c79646572_01.html
            case ("bl" | "mailorder"),  ("cot" | "cit" | "ebk"), "circle", _, _, _circle_id, _:
                instance = ToranoanaOldCircleUrl(parsable_url)

            # http://dl.toranoana.jp/cgi-bin/coterie_item_search.cgi?circle=00004202270200000001
            case "cgi-bin", "coterie_item_search.cgi":
                instance = ToranoanaOldCircleUrl(parsable_url)

            # https://contents.toranoana.jp/ec/tora_r/cit/temp/00181/typea/C94_%E3%81%8D%E3%82%93%E3%81%8F_a.jpg
            case "ec", "tora_r", "cit", "temp", _, "typea", _:
                raise UnparsableUrlError(parsable_url)

            # http://www.toranoana.jp/webcomic/holic/news/20080501_yayoi_01.jpg
            case "webcomic", "holic", "news", _:
                raise UnparsableUrlError(parsable_url)

            # https://www.toranoana.jp/info/media/monmusu/fair06.html
            # https://www.toranoana.jp/info/etc/090814_gensou/img_top/main.jpg
            # http://www.toranoana.jp/info/hobby/touhou_gacha/batch04/mochi.jpg
            case "info", *_:
                raise UnparsableUrlError(parsable_url)

            # http://www.toranoana.jp/coco2/illust/toradayo/img/0050.jpg
            case _, "illust", _, "img", _:
                raise UnparsableUrlError(parsable_url)

            # http://www.toranoana.jp/bl/toranomori/illust/img/0102.jpg
            case "bl", "toranomori", "illust", "img", _:
                raise UnparsableUrlError(parsable_url)

            # https://ec.toranoana.jp/tora_r/ec/cit/pages/temp-00101/00181
            case _, ("ec" | "digi"), ("cot" | "cit" | "ebk"), "pages", _, _:
                raise UnparsableUrlError(parsable_url)

            # http://www.toranoana.jp/mailorder/cot/pagekit/0000/00/07/000000077654/index.html
            # http://www.toranoana.jp/mailorder/cit/pagekit/0000/02/59/0000025956/040010201387-02al.jpg
            case  ("bl" | "mailorder"), ("cot" | "cit" | "ebk"), "pagekit", _, _, _, _, _:
                raise UnparsableUrlError(parsable_url)

            # http://www.toranoana.jp/cgi-bin/R2/d_search.cgi?bl_fg=0\u0026item_kind=0402\u0026mak=eb\u0026img=1\u0026stk=1\u0026makAg=1\u0026p1=\u0026p2=\u0026p3=
            case "cgi-bin", "R2", "d_search.cgi":
                return UselessUrl(parsable_url)

            case _:
                return None

        return instance
