import re
from urllib.parse import unquote

from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors import fanza as fz
from danboorutools.logical.parsers import ParsableUrl, UrlParser

filename_pattern = re.compile(r"^(\w+)\w{2}(?:-(\d+))?\.\w+$")


class DmmCoJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> fz.FanzaUrl | None:
        if parsable_url.subdomain in ["www", "", "sp"]:
            if parsable_url.url_parts[0] == "en":
                return cls._match_www_subdomain(ParsableUrl(parsable_url.raw_url.replace("/en/", "/")))
            else:
                return cls._match_www_subdomain(parsable_url)

        elif parsable_url.subdomain == "dlsoft":
            return cls._match_dlsoft_subdomain(parsable_url)

        elif parsable_url.subdomain == "book":
            return cls._match_book_subdomain(parsable_url)

        elif parsable_url.subdomain == "games":
            return cls._match_games_subdomain(parsable_url)

        elif parsable_url.subdomain in ["doujin-assets", "pics", "ebook-assets", "media.games", "p"]:
            return cls._match_images(parsable_url)

        # https://al.dmm.co.jp/?lurl=https%3A%2F%2Fwww.dmm.co.jp%2Fdc%2Fdoujin%2F-%2Fdetail%2F%3D%2Fcid%3Dd_218503%2F&af_id=conoco-002
        elif parsable_url.subdomain == "al":
            param_url = parsable_url.query["lurl"]
            unquoted_url = unquote(param_url)
            return cls.parse(unquoted_url)  # type: ignore[return-value]

        # http://p-xtasy.dmm.co.jp/img/web/girls/635490047292404333.png
        elif parsable_url.subdomain == "p-xtasy":
            raise UnparsableUrl(parsable_url)

        elif parsable_url.hostname == "ad.games.dmm.co.jp":  # could have any html page
            raise UnparsableUrl(parsable_url)

        else:
            return None

    @classmethod
    def _match_www_subdomain(cls, parsable_url: ParsableUrl) -> fz.FanzaUrl | None:
        instance: fz.FanzaUrl

        match parsable_url.url_parts:
            # https://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_218503/
            # https://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_cs0949/
            case ("dc" | "digital" | "mono") as subsubsite, "doujin", "-", "detail", "=", _f, *_:
                instance = fz.FanzaDoujinWorkUrl(parsable_url)
                instance.work_id = _f.removeprefix("cid=")
                instance.subsubsite = subsubsite

            # http://www.dmm.co.jp/digital/doujin/-/list/=/article=maker/id=27726/
            # https://www.dmm.co.jp/dc/doujin/-/list/=/article=maker/id=70980
            case ("dc" | "digital" | "mono") as subsubsite, "doujin", "-", "list", "=", "article=maker", _f, *_:
                instance = fz.FanzaDoujinAuthorUrl(parsable_url)
                instance.user_id = int(_f.removeprefix("id="))
                instance.subsubsite = subsubsite

            # http://www.dmm.co.jp/dc/book/-/list/=/article=author/id=254530/media=comic
            # http://www.dmm.co.jp/digital/book/-/list/=/article=author/id=240536/media=comic/
            # https://www.dmm.co.jp/mono/book/-/list/=/article=author/id=240684/
            case ("dc" | "digital" | "mono"), "book", "-", "list", "=", "article=author", slug, *_:
                instance = fz.FanzaBookAuthorUrl(parsable_url)
                instance.user_id = int(slug.split("=")[-1])

            # http://www.dmm.co.jp/dc/book/-/detail/=/cid=b073bktcm00445/
            case ("dc" | "digital"), "book", "-", "detail", "=", slug:
                instance = fz.FanzaBookNoSeriesUrl(parsable_url)
                instance.work_id = slug.split("=")[-1]

            # https://www.dmm.co.jp/mono/book/-/detail/=/cid=204book18118122016/
            # thanks to western retards, this cannot be normalized because it's jp only (loli)
            case "mono", "book", "-", "detail", "=", slug:
                instance = fz.FanzaBookWorkUrl(parsable_url)
                instance.work_id = slug.split("=")[-1]
                instance.series_id = None

            # http://www.dmm.co.jp/digital/pcgame/-/detail/=/cid=tech_0003/
            case "digital", "pcgame", "-", "detail", "=", slug:
                instance = fz.FanzaDlsoftWorkUrl(parsable_url)
                instance.work_id = slug.split("=")[-1]

            # http://sp.dmm.co.jp/netgame/application/detail/app_id/968828
            case "netgame", "application", "detail", "app_id", game_id:
                instance = fz.FanzaGamesOldGameUrl(parsable_url)
                instance.game_id = int(game_id)

            # http://www.dmm.co.jp/netgame_s/flower-x
            case "netgame_s", game_name:
                instance = fz.FanzaGamesGameUrl(parsable_url)
                instance.game_name = game_name

            # http://www.dmm.co.jp/en/digital/nijigen/mlmg_present/120720/page_siratama.html/
            case *_, "digital", "nijigen", "mlmg_present", _, _:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance

    @staticmethod
    def _match_dlsoft_subdomain(parsable_url: ParsableUrl) -> fz.FanzaUrl | None:
        instance: fz.FanzaUrl

        match parsable_url.url_parts:
            # https://dlsoft.dmm.co.jp/detail/jveilelwy_0001/
            case "detail", work_id:
                instance = fz.FanzaDlsoftWorkUrl(parsable_url)
                instance.work_id = work_id

            # https://dlsoft.dmm.co.jp/list/article=maker/id=30267/
            # http://dlsoft.dmm.co.jp/list/article=author/id=239811/
            case "list", ("article=maker" | "article=author") as user_type, slug:
                instance = fz.FanzaDlsoftAuthorUrl(parsable_url)
                instance.user_id = int(slug.split("=")[-1])
                instance.user_type = user_type

            # http://dlsoft.dmm.co.jp/elf/elfall/index/
            case _, _, "index":
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance

    @staticmethod
    def _match_book_subdomain(parsable_url: ParsableUrl) -> fz.FanzaUrl | None:
        instance: fz.FanzaUrl

        match parsable_url.url_parts:
            # https://book.dmm.co.jp/product/761338/b472abnen00334/
            case "product", series_id, book_id:
                instance = fz.FanzaBookWorkUrl(parsable_url)
                instance.series_id = int(series_id)
                instance.work_id = book_id

            # https://book.dmm.co.jp/list/?author=254530
            case "list", :
                instance = fz.FanzaBookAuthorUrl(parsable_url)
                instance.user_id = int(parsable_url.query["author"])

            # http://book.dmm.co.jp/author/256941/
            # https://book.dmm.co.jp/author/238380/OBBM-001
            case "author", author_id, *_:
                instance = fz.FanzaBookAuthorUrl(parsable_url)
                instance.user_id = int(author_id)

            # http://book.dmm.co.jp/list/comic/?floor=Abook\u0026article=author\u0026id=257051\u0026type=single
            # http://book.dmm.co.jp/list/comic/?floor=Abook\u0026article=author\u0026id=25105/
            case "list", "comic" if parsable_url.query["article"] == "author":
                instance = fz.FanzaBookAuthorUrl(parsable_url)
                instance.user_id = int(parsable_url.query["id"].strip("/"))

            # http://book.dmm.co.jp/detail/b915awnmg00690/
            # http://book.dmm.co.jp/detail/b061bangl00828/ozy3jyayo-001
            case "detail", work_id, *_:
                instance = fz.FanzaBookNoSeriesUrl(parsable_url)
                instance.work_id = work_id

            case _:
                return None

        return instance

    @staticmethod
    def _match_games_subdomain(parsable_url: ParsableUrl) -> fz.FanzaUrl | None:
        instance: fz.FanzaUrl

        match parsable_url.url_parts:
            # https://games.dmm.co.jp/detail/devilcarnival
            case "detail", game_name:
                instance = fz.FanzaGamesGameUrl(parsable_url)
                instance.game_name = game_name

            case _:
                return None

        return instance

    @staticmethod
    def _match_images(parsable_url: ParsableUrl) -> fz.FanzaImageUrl | None:
        match parsable_url.url_parts:
            # https://doujin-assets.dmm.co.jp/digital/comic/d_261113/d_261113pl.jpg
            # https://doujin-assets.dmm.co.jp/digital/comic/d_218503/d_218503pr.jpg
            # https://doujin-assets.dmm.co.jp/digital/comic/d_261113/d_261113jp-001.jpg
            # https://pics.dmm.co.jp/mono/comic/420abgoods022/420abgoods022pl.jpg
            # https://pics.dmm.co.jp/mono/doujin/d_d0014920/d_d0014920jp-002.jpg
            case ("mono" | "digital"), ("comic" | "doujin"), _, _filename:
                instance = fz.FanzaImageUrl(parsable_url)
                instance.work_type = "doujin"

                match = filename_pattern.match(_filename)

            # https://pics.dmm.co.jp/digital/pcgame/jveilelwy_0001/jveilelwy_0001pl.jpg
            # https://pics.dmm.co.jp/digital/pcgame/jveilelwy_0001/jveilelwy_0001jp-001.jpg
            case "digital", "pcgame", work_id, _filename:
                instance = fz.FanzaImageUrl(parsable_url)
                instance.work_type = "dlsoft"
                instance.work_id = work_id
                match = filename_pattern.match(_filename)

            # https://ebook-assets.dmm.co.jp/digital/e-book/b472abnen00169/b472abnen00169pl.jpg
            case "digital", "e-book", book_id, _filename:
                instance = fz.FanzaImageUrl(parsable_url)
                instance.work_type = "book"
                instance.page = 0
                instance.work_id = book_id
                return instance

            # https://media.games.dmm.co.jp/freegame/app/968828/968828sp_01.jpg
            case "freegame", "app", game_id, _filename:
                instance = fz.FanzaImageUrl(parsable_url)
                instance.work_type = "freegame"
                instance.work_id = game_id
                match = filename_pattern.match(_filename)

            # http://p.dmm.co.jp/p/netgame/feature/gemini/cp_02_chara_01.png
            case "p", "netgame", "feature", game_name, _filename:
                instance = fz.FanzaImageUrl(parsable_url)
                instance.work_type = "netgame"
                instance.work_id = game_name
                instance.page = 0
                return instance

            # https://pics.dmm.co.jp/mono/goods/ho5761/ho5761jp-007.jpg
            case "mono", "goods", _good_id, _filename:
                instance = fz.FanzaImageUrl(parsable_url)
                instance.work_type = "good"
                match = filename_pattern.match(_filename)

            # http://pics.dmm.co.jp/mono/game/1927apc10857/1927apc10857pl.jpg
            case "mono", "game", game_id, _filename:
                instance = fz.FanzaImageUrl(parsable_url)
                instance.work_type = "dlsoft"
                match = filename_pattern.match(_filename)

            # http://pics.dmm.co.jp/digital/video/66nov08380/66nov08380pl.jpg
            case "digital", "video", _video_id, _filename:
                instance = fz.FanzaImageUrl(parsable_url)
                instance.work_type = "video"
                match = filename_pattern.match(_filename)

            case _:
                return None

        if not match:
            raise NotImplementedError(parsable_url, match)
        instance.work_id = match.groups()[0]
        instance.page = int(groups[1]) if len(groups := match.groups()) > 1 and groups[1] else 0
        return instance
