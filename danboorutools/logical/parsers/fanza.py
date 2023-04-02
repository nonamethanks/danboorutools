import re
from urllib.parse import unquote

from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import fanza as fz

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
            raise UnparsableUrlError(parsable_url)

        elif parsable_url.hostname == "ad.games.dmm.co.jp":  # could have any html page
            raise UnparsableUrlError(parsable_url)

        else:
            return None

    @classmethod
    def _match_www_subdomain(cls, parsable_url: ParsableUrl) -> fz.FanzaUrl | None:
        match parsable_url.url_parts:
            # https://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_218503/
            # https://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_cs0949/
            case ("dc" | "digital" | "mono") as subsubsite, "doujin", "-", "detail", "=", _f, *_:
                return fz.FanzaDoujinWorkUrl(parsed_url=parsable_url,
                                             work_id=_f.removeprefix("cid="),
                                             subsubsite=subsubsite)

            # http://www.dmm.co.jp/digital/doujin/-/list/=/article=maker/id=27726/
            # https://www.dmm.co.jp/dc/doujin/-/list/=/article=maker/id=70980
            case ("dc" | "digital" | "mono") as subsubsite, "doujin", "-", "list", "=", "article=maker", _f, *_:
                return fz.FanzaDoujinAuthorUrl(parsed_url=parsable_url,
                                               user_id=int(_f.removeprefix("id=")),
                                               subsubsite=subsubsite)

            # http://www.dmm.co.jp/dc/book/-/list/=/article=author/id=254530/media=comic
            # http://www.dmm.co.jp/digital/book/-/list/=/article=author/id=240536/media=comic/
            # https://www.dmm.co.jp/mono/book/-/list/=/article=author/id=240684/
            case ("dc" | "digital" | "mono"), "book", "-", "list", "=", "article=author", slug, *_:
                return fz.FanzaBookAuthorUrl(parsed_url=parsable_url,
                                             user_id=int(slug.split("=")[-1]))

            # http://www.dmm.co.jp/dc/book/-/detail/=/cid=b073bktcm00445/
            case ("dc" | "digital"), "book", "-", "detail", "=", slug:
                return fz.FanzaBookNoSeriesUrl(parsed_url=parsable_url,
                                               work_id=slug.split("=")[-1])

            # https://www.dmm.co.jp/mono/book/-/detail/=/cid=204book18118122016/
            # thanks to western retards, this cannot be normalized because it's jp only (loli)
            case "mono", "book", "-", "detail", "=", slug:
                return fz.FanzaBookWorkUrl(parsed_url=parsable_url,
                                           work_id=slug.split("=")[-1],
                                           series_id=None)

            # http://www.dmm.co.jp/digital/pcgame/-/detail/=/cid=tech_0003/
            # https://www.dmm.co.jp/mono/pcgame/-/detail/=/cid=1001tb044/
            case ("digital" | "mono") as subsubsite, "pcgame", "-", "detail", "=", slug:
                return fz.FanzaDlsoftWorkUrl(parsed_url=parsable_url,
                                             work_id=slug.split("=")[-1],
                                             subsubsite=subsubsite)

            # http://sp.dmm.co.jp/netgame/application/detail/app_id/968828
            case "netgame", "application", "detail", "app_id", game_id:
                return fz.FanzaGamesOldGameUrl(parsed_url=parsable_url,
                                               game_id=int(game_id))

            # http://www.dmm.co.jp/netgame_s/flower-x
            case "netgame_s", game_name:
                return fz.FanzaGamesGameUrl(parsed_url=parsable_url,
                                            game_name=game_name)

            # http://www.dmm.co.jp/en/digital/nijigen/mlmg_present/120720/page_siratama.html/
            case *_, "digital", "nijigen", "mlmg_present", _, _:
                raise UnparsableUrlError(parsable_url)

            case _:
                return None

    @staticmethod
    def _match_dlsoft_subdomain(parsable_url: ParsableUrl) -> fz.FanzaUrl | None:
        match parsable_url.url_parts:
            # https://dlsoft.dmm.co.jp/detail/jveilelwy_0001/
            case "detail", work_id:
                return fz.FanzaDlsoftWorkUrl(parsed_url=parsable_url,
                                             subsubsite="digital",
                                             work_id=work_id)

            # https://dlsoft.dmm.co.jp/list/article=maker/id=30267/
            # http://dlsoft.dmm.co.jp/list/article=author/id=239811/
            case "list", ("article=maker" | "article=author") as user_type, slug:
                return fz.FanzaDlsoftAuthorUrl(parsed_url=parsable_url,
                                               user_id=int(slug.split("=")[-1]),
                                               user_type=user_type)

            # http://dlsoft.dmm.co.jp/elf/elfall/index/
            case _, _, "index":
                raise UnparsableUrlError(parsable_url)

            case _:
                return None

    @staticmethod
    def _match_book_subdomain(parsable_url: ParsableUrl) -> fz.FanzaUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://book.dmm.co.jp/product/761338/b472abnen00334/
            case "product", series_id, book_id:
                return fz.FanzaBookWorkUrl(parsed_url=parsable_url,
                                           series_id=int(series_id),
                                           work_id=book_id)

            # https://book.dmm.co.jp/list/?author=254530
            case "list", :
                return fz.FanzaBookAuthorUrl(parsed_url=parsable_url,
                                             user_id=int(parsable_url.query["author"]))

            # http://book.dmm.co.jp/author/256941/
            # https://book.dmm.co.jp/author/238380/OBBM-001
            case "author", author_id, *_:
                return fz.FanzaBookAuthorUrl(parsed_url=parsable_url,
                                             user_id=int(author_id))

            # http://book.dmm.co.jp/list/comic/?floor=Abook\u0026article=author\u0026id=257051\u0026type=single
            # http://book.dmm.co.jp/list/comic/?floor=Abook\u0026article=author\u0026id=25105/
            case "list", "comic" if parsable_url.query["article"] == "author":
                return fz.FanzaBookAuthorUrl(parsed_url=parsable_url,
                                             user_id=int(parsable_url.query["id"].strip("/")))

            # http://book.dmm.co.jp/detail/b915awnmg00690/
            # http://book.dmm.co.jp/detail/b061bangl00828/ozy3jyayo-001
            case "detail", work_id, *_:
                return fz.FanzaBookNoSeriesUrl(parsed_url=parsable_url,
                                               work_id=work_id)

            case _:
                return None

    @staticmethod
    def _match_games_subdomain(parsable_url: ParsableUrl) -> fz.FanzaUrl | None:
        match parsable_url.url_parts:
            # https://games.dmm.co.jp/detail/devilcarnival
            case "detail", game_name:
                return fz.FanzaGamesGameUrl(parsed_url=parsable_url,
                                            game_name=game_name)

            case _:
                return None

    @staticmethod
    def _match_images(parsable_url: ParsableUrl) -> fz.FanzaImageUrl | None:
        match parsable_url.url_parts:
            # https://doujin-assets.dmm.co.jp/digital/comic/d_261113/d_261113pl.jpg
            # https://doujin-assets.dmm.co.jp/digital/comic/d_218503/d_218503pr.jpg
            # https://doujin-assets.dmm.co.jp/digital/comic/d_261113/d_261113jp-001.jpg
            # https://pics.dmm.co.jp/mono/comic/420abgoods022/420abgoods022pl.jpg
            # https://pics.dmm.co.jp/mono/doujin/d_d0014920/d_d0014920jp-002.jpg
            case ("mono" | "digital"), ("comic" | "doujin"), _, _filename:
                work_type = "doujin"
                match = filename_pattern.match(_filename)

            # https://pics.dmm.co.jp/digital/pcgame/jveilelwy_0001/jveilelwy_0001pl.jpg
            # https://pics.dmm.co.jp/digital/pcgame/jveilelwy_0001/jveilelwy_0001jp-001.jpg
            case "digital", "pcgame", _work_id, _filename:
                work_type = "dlsoft"
                match = filename_pattern.match(_filename)

            # https://ebook-assets.dmm.co.jp/digital/e-book/b472abnen00169/b472abnen00169pl.jpg
            case "digital", "e-book", book_id, _filename:
                return fz.FanzaImageUrl(parsed_url=parsable_url,
                                        work_type="book",
                                        page=0,
                                        work_id=book_id)

            # https://media.games.dmm.co.jp/freegame/app/968828/968828sp_01.jpg
            case "freegame", "app", _game_id, _filename:
                work_type = "freegame"
                match = filename_pattern.match(_filename)

            # http://p.dmm.co.jp/p/netgame/feature/gemini/cp_02_chara_01.png
            case "p", "netgame", "feature", game_name, _filename:
                return fz.FanzaImageUrl(parsed_url=parsable_url,
                                        work_type="netgame",
                                        work_id=game_name,
                                        page=0)

            # https://pics.dmm.co.jp/mono/goods/ho5761/ho5761jp-007.jpg
            case "mono", "goods", _good_id, _filename:
                work_type = "good"
                match = filename_pattern.match(_filename)

            # http://pics.dmm.co.jp/mono/game/1927apc10857/1927apc10857pl.jpg
            case "mono", "game", _game_id, _filename:
                work_type = "dlsoft"
                match = filename_pattern.match(_filename)

            # http://pics.dmm.co.jp/digital/video/66nov08380/66nov08380pl.jpg
            case "digital", "video", _video_id, _filename:
                work_type = "video"
                match = filename_pattern.match(_filename)

            case _:
                return None

        if not match:
            raise NotImplementedError(parsable_url, match)
        work_id = match.groups()[0]
        page = int(groups[1]) if len(groups := match.groups()) > 1 and groups[1] else 0

        return fz.FanzaImageUrl(parsed_url=parsable_url,
                                work_type=work_type,  # type: ignore[arg-type]
                                work_id=work_id,
                                page=page)
