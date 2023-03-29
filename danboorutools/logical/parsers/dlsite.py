import re
from urllib.parse import unquote

from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.dlsite import DlsiteAuthorUrl, DlsiteImageUrl, DlsiteKeywordSearch, DlsiteUrl, DlsiteWorkUrl
from danboorutools.logical.urls.dlsite_cien import DlsiteCienArticleUrl, DlsiteCienCreatorUrl, DlsiteCienProfileUrl, DlsiteCienUrl


class DlsiteComParser(UrlParser):
    CIRCLE_SUBSITES = ("maniax", "ecchi-eng", "bl", "gay", "girls", "home", "eng", "pro", "books")
    SUBSITE_ALIASES = {
        "ecchi-eng": "maniax",
        "eng": "home",
        "gay": "bl",  # no homo
        "girls-pro": "girls",
    }
    KEYWORD_MAKER_NAME_PATTERN = re.compile(r"((?:AJ|RG)\d+)$")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DlsiteUrl | DlsiteCienUrl | None:
        if parsable_url.subdomain == "ci-en":
            return cls._match_cien(parsable_url)
        elif parsable_url.subdomain in cls.CIRCLE_SUBSITES:
            return cls._match_main(parsable_url, parsable_url.subdomain, *parsable_url.url_parts)
        else:
            return cls._match_main(parsable_url, *parsable_url.url_parts)

    @classmethod
    def _match_main(cls, parsable_url: ParsableUrl, *url_parts: str) -> DlsiteUrl | None:  # type: ignore[return]
        subsite = url_parts[0].removesuffix("-touch")
        subsite = cls.SUBSITE_ALIASES.get(subsite, subsite)

        match url_parts:
            # https://www.dlsite.com/books/author/=/author_id/AJ002787
            case _, "author", "=", "author_id", author_id:
                return DlsiteAuthorUrl(parsed_url=parsable_url,
                                       author_id=parsable_url.stem,
                                       subsite=subsite)  # type: ignore[arg-type]

            # https://www.dlsite.com/books/work/=/product_id/BJ115183
            # https://www.dlsite.com/girls/work/=/product_id/RJ01023665.html
            # https://www.dlsite.com/bl/work/=/product_id/RJ01013942.html
            # http://maniax.dlsite.com/work/=/product_id/RJ065490.html
            # http://maniax.dlsite.com/work/=/product_site/1/product_id/RJ025429.html
            # https://www.dlsite.com/maniax/announce/=/product_id/RJ180508.html  # announcement
            case _, ("work" | "announce") as status, "=", *_, "product_id", _work_id:
                return DlsiteWorkUrl(parsed_url=parsable_url,
                                     work_id=parsable_url.stem,
                                     status=status,
                                     subsite=subsite)  # type: ignore[arg-type]

            # https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG28852.html
            # https://www.dlsite.com/ecchi-eng/circle/profile/=/maker_id/RG12762.html
            # https://www.dlsite.com/girls/circle/profile/=/maker_id/RG67968.html
            # https://www.dlsite.com/bl/circle/profile/=/maker_id/RG58534.html
            # http://www.dlsite.com/home/circle/profile/=/maker_id/RG27185.html
            # http://maniax.dlsite.com/circle/profile/=/maker_id/RG12065.html
            # http://www.dlsite.com/pro/circle/profile/=/maker_id/VG01352
            # https://www.dlsite.com/eng/circle/profile/=/maker_id/RG24167.html
            # http://www.dlsite.com/gay/circle/profile/=/maker_id/RG13474.html
            # http://www.dlsite.com/gay-touch/circle/profile/=/from/work.maker/maker_id/RG35592.html
            # http://www.dlsite.com/maniax-touch/circle/profile/=/from/work.maker/maker_id/RG36965.html
            case _, "circle", "profile", "=", *_, "maker_id", author_id:
                return DlsiteAuthorUrl(parsed_url=parsable_url,
                                       author_id=parsable_url.stem,
                                       subsite=subsite)  # type: ignore[arg-type]

            # http://maniax.dlsite.com/fsr/=/kw/RG06677/od/reg_d
            # https://www.dlsite.com/maniax/fsr/=/kw/RG06677/od/reg_d
            # https://www.dlsite.com/maniax/fsr/=/kw/RG29700/
            case _, "fsr", "=", "kw", author_id, *_:
                return DlsiteAuthorUrl(parsed_url=parsable_url,
                                       author_id=author_id,
                                       subsite=subsite)  # type: ignore[arg-type]

            case _, "fsr", "=", "keyword_maker_name", unicode_mess, *_:
                unicode_mess = unquote(unicode_mess)

                # http://www.dlsite.com/books/fsr/=/keyword_maker_name/%B8%A4%C0%B1%20AJ002493
                # http://www.dlsite.com/books/fsr/=/keyword_maker_name/%BF%DC%C6%A3%A4%EB%A4%AF%20AJ001613/from/work.author
                # http://www.dlsite.com/books/fsr/=/keyword_maker_name/丹羽香ゆあん+AJ003398/
                # http://www.dlsite.com/books/fsr/=/keyword_maker_name/AJ005866/
                # http://www.dlsite.com/maniax/fsr/=/keyword_maker_name/空道へのR%20RG25050/ana_flg/all/from/work.same_maker
                if match := cls.KEYWORD_MAKER_NAME_PATTERN.search(unicode_mess):
                    return DlsiteAuthorUrl(parsed_url=parsable_url,
                                           author_id=match.groups()[0],
                                           subsite=subsite)  # type: ignore[arg-type]

                else:
                    return None

            # https://www.dlsite.com/maniax/dlaf/=/link/profile/aid/sotokanda/maker/RG03905.html
            case _, "dlaf", "=", "link", "profile", *_, "maker", author_id:
                return DlsiteAuthorUrl(parsed_url=parsable_url,
                                       author_id=parsable_url.stem,
                                       subsite=subsite)  # type: ignore[arg-type]

            # http://www.dlsite.com/maniax/dlaf/=/link/work/aid/tbnb/id/RJ109634.html
            # https://www.dlsite.com/girls-pro/dlaf/=/link/work/aid/conoco01/id/BJ327214.html
            case _, "dlaf", "=", "link", "work", *_, "id", _work_id:
                return DlsiteWorkUrl(parsed_url=parsable_url,
                                     work_id=parsable_url.stem,
                                     status="work",
                                     subsite=subsite)  # type: ignore[arg-type]

            # https://www.dlsite.com/maniax/dlaf/=/t/s/link/work/aid/yuen/locale/en_US/id/RJ326899.html/?locale=en_US
            case _, "dlaf", "=", "t", "s", "link", "work", *_, "id", _work_id:
                # type: ignore[arg-type]
                return DlsiteWorkUrl(parsed_url=parsable_url,
                                     work_id=parsable_url.stem,
                                     status="work",
                                     subsite=subsite)  # type: ignore[arg-type]

            # https://www.dlsite.com/maniax/fsr/=/keyword_creater/"灰葉"
            case _, "fsr", "=", "keyword_creater", keyword:
                return DlsiteKeywordSearch(parsable_url,
                                           keyword=keyword.strip("\"'"),
                                           subsite=subsite)  # type: ignore[arg-type]

            # http://maniax.dlsite.com/modpub/images2/work/doujin/RJ032000/RJ031102_img_smp1.jpg
            case *_, "images2", ("work" | "ana") as status, "doujin", _, _filename:
                return DlsiteImageUrl(parsed_url=parsable_url,
                                      subsite="doujin",
                                      status=status,
                                      work_id=_filename.split("_")[0])

            # http://maniax.dlsite.com/modpub/images/character/0907_maniax_1600.jpg
            # http://www.dlsite.com/modpub/images/character/1204_maniax_w1920.jpg
            # http://home.dlsite.com/modpub/images/character/0908_maniax_1600.jpg # TODO: maybe i should check if these unparsable sources are all uploaded at max res
            case *_, "modpub", "images", "character", _filename:
                raise UnparsableUrlError(parsable_url)

            # http://www.dlsite.com/images/character/wallpaper/1605_maniax_w1920.jpg
            case *_, "images", "character", "wallpaper", _filename:
                raise UnparsableUrlError(parsable_url)

            # http://www.dlsite.com/images/event/wallpaper_present_girls/20170430/wallpaper_1920x1200.jpg
            case *_, "images", "event", "wallpaper_present_girls", _, _:
                raise UnparsableUrlError(parsable_url)

            # http://www.dlsite.com/work/workshow.cgi?workno=pa2104
            case *_, "work", "workshow.cgi":
                raise UnparsableUrlError(parsable_url)

            # https://media.dlsite.com/proxy/41a63a3bed0252225347604b2bb53ebd6aa37487/687474703a2f2f68656e7461697472656e63682e636f6d2f696d616765732f6269675f696d616765732f323031342f30372f32392f637574652d7363686f6f6c6769726c2d31373031352e6a7067
            case *_, "proxy", _, _ if parsable_url.hostname == "media.dlsite.com":
                raise UnparsableUrlError(parsable_url)

            # https://media.dlsite.com/chobit/contents/0907/ckn20nx8gbsos4g408kgk0sk0/ckn20nx8gbsos4g408kgk0sk0_020.jpg
            case *_, "chobit", "contents", _, _, _ if parsable_url.hostname == "media.dlsite.com":
                raise UnparsableUrlError(parsable_url)

            # http://home.dlsite.com/dlaf/=/aid/iisearch/url/http%253A%252F%252Fmaniax.dlsite.com%252Fwork%252F%253D%252Fproduct_id%252FRJ034344.html
            case *_, "dlaf", "=", "aid", "iisearch", "url", encoded_url:
                unquoted_url = unquote(unquote(encoded_url))
                return cls.parse(unquoted_url)  # type: ignore[return-value]

            case *_, "error.html":
                raise UnparsableUrlError(parsable_url)

            case _:
                return None

    @ classmethod
    def _match_cien(cls, parsable_url: ParsableUrl) -> DlsiteCienUrl | None:
        match parsable_url.url_parts:
            # https://ci-en.dlsite.com/creator/3894/article/684012
            case "creator", creator_id, "article", article_id:
                return DlsiteCienArticleUrl(parsed_url=parsable_url,
                                            creator_id=int(creator_id),
                                            article_id=int(article_id))

            # https://ci-en.dlsite.com/creator/3894
            # https://ci-en.dlsite.com/creator/12346/shop
            case "creator", creator_id, *_:
                return DlsiteCienCreatorUrl(parsed_url=parsable_url,
                                            creator_id=int(creator_id))

            case "profile", profile_id:
                return DlsiteCienProfileUrl(parsed_url=parsable_url,
                                            profile_id=int(profile_id))

            case _:
                return None


class DlsiteJpParser(UrlParser):
    SUBSITE_ALIASES = {
        "mawtw": "maniax",
        "howtw": "home",
    }

    @ classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> DlsiteUrl | None:
        match parsable_url.url_parts:
            # https://img.dlsite.jp/resize/images2/work/books/BJ007000/BJ006925_img_main_240x240.jpg
            # https://img.dlsite.jp/modpub/images2/work/books/BJ007000/BJ006925_img_main.jpg
            # https://img.dlsite.jp/modpub/images2/work/books/BJ007000/BJ006925_img_main.webp
            # https://img.dlsite.jp/modpub/images2/work/books/BJ007000/BJ006925_img_smp1.jpg
            case _, "images2", "work", "books", _, _filename:
                return DlsiteImageUrl(parsed_url=parsable_url,
                                      subsite="books",
                                      status="work",
                                      work_id=_filename.split("_")[0])
            # https://img.dlsite.jp/resize/images2/work/doujin/RJ01014000/RJ01013942_img_main_240x240.jpg
            # https://img.dlsite.jp/modpub/images2/ana/doujin/RJ181000/RJ180508_ana_img_main.webp
            # https://img.dlsite.jp/modpub/images2/work/doujin/RJ032000/RJ031102_img_smp1.jpg
            case _, "images2", ("work" | "ana") as status, "doujin", _, _filename:
                return DlsiteImageUrl(parsed_url=parsable_url,
                                      subsite="doujin",
                                      status=status,
                                      work_id=_filename.split("_")[0])

            # https://img.dlsite.jp/modpub/images2/parts/RJ278000/RJ277383/RJ277383_PTS0000021229_0.jpg
            case _, "images2", ("parts" | "parts_ana") as status, _, _, _filename:
                return DlsiteImageUrl(parsed_url=parsable_url,
                                      subsite="doujin",
                                      status="work" if status == "parts" else "ana",
                                      work_id=_filename.split("_")[0])

            # http://dlsite.jp/mawtw/RJ198108
            # http://dlsite.jp/howtw/RJ219372
            case ("mawtw" | "howtw") as subsite, work_id:
                return DlsiteWorkUrl(parsed_url=parsable_url,
                                     subsite=cls.SUBSITE_ALIASES[subsite],  # type: ignore[arg-type]
                                     work_id=work_id.removesuffix(".html"),
                                     status="work")

            case _:
                return None
