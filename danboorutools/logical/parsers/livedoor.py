import re

from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import livedoor as ld
from danboorutools.models.url import UnsupportedUrl


class LivedoorJpParser(UrlParser):
    blog_img_pattern = re.compile(r"^\w+(-s)?\.(?:gif|jpe?g|png)$", re.I)

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ld.LivedoorUrl | UnsupportedUrl | None:
        if parsable_url.subdomain in ["blog", "blog.m", "image.blog"]:
            return cls._parse_blog(parsable_url=parsable_url)
        elif parsable_url.subdomain.endswith(".aaa"):
            return cls._parse_aaa(parsable_url=parsable_url)
        elif parsable_url.subdomain == "jbbs" or parsable_url.subdomain.endswith(".jbbs"):
            return UnsupportedUrl(parsed_url=parsable_url)
        elif parsable_url.subdomain in ["wiki", "image01.w"] or parsable_url.subdomain.endswith(".wiki"):
            return UnsupportedUrl(parsed_url=parsable_url)
        else:
            return None

    @classmethod
    def _parse_blog(cls, parsable_url: ParsableUrl) -> ld.LivedoorUrl | UnsupportedUrl | None:
        match parsable_url.url_parts:
            # http://blog.livedoor.jp/rubbercorn5/
            case username, :
                return ld.LivedoorBlogUrl(parsed_url=parsable_url,
                                          username=username)

            # http://blog.livedoor.jp/okuirafan/search?q=momohiyaltuko0124
            # http://blog.livedoor.jp/tokunaga3046/lite/
            case username, ("search" | "lite"):
                return ld.LivedoorBlogUrl(parsed_url=parsable_url,
                                          username=username)

            # http://blog.livedoor.jp/geek/tag/サークル綿120パーセント
            case username, "tag", _tag_name:
                return ld.LivedoorBlogUrl(parsed_url=parsable_url,
                                          username=username)

            # http://blog.livedoor.jp/nobujyamira/archives/2167208.html/
            # http://blog.livedoor.jp/jyugemu125/archives/cat_19311.html/
            # http://blog.livedoor.jp/dowman/archives/457319.htm
            # http://blog.livedoor.jp/cosax/archives/44477406.html#more
            # http://blog.livedoor.jp/xxx0w/archives/51508589.html#comments
            case username, "archives", html_page:
                if re.match(r"^cat_\d+\.html?$", html_page.split("#")[0]):
                    return ld.LivedoorBlogUrl(parsed_url=parsable_url,
                                              username=username)

                elif match := re.match(r"^(\d+)\.html?$", html_page.split("#")[0]):
                    return ld.LivedoorBlogArchiveUrl(parsed_url=parsable_url,
                                                     username=username,
                                                     post_id=int(match.groups()[0]))

                # http://blog.livedoor.jp/bkub/archives/2008-03.html
                elif match := re.match(r"^\d{4}-\d{2}\.html$", html_page):
                    return UnsupportedUrl(parsed_url=parsable_url)

                else:
                    return None

            # http://image.blog.livedoor.jp/m-54_25833/imgs/0/e/0e33df5d-s.jpg
            # http://image.blog.livedoor.jp/chikubige/imgs/8/d/8dfb5d0c.gif
            case username, "imgs", f1, f2, filename if len(f1) == 1 and len(f2) == 1 and cls.blog_img_pattern.match(filename):
                return ld.LivedoorImageUrl(parsed_url=parsable_url,
                                           username=username)

            # http://blog.livedoor.jp/ribido88/imgs/8/7/
            case username, "imgs", f1, f2 if len(f1) == 1 and len(f2) == 1:
                return ld.LivedoorBlogUrl(parsed_url=parsable_url,
                                          username=username)

            # http://image.blog.livedoor.jp/megadriv/imgs/
            case username, "imgs":
                return ld.LivedoorBlogUrl(parsed_url=parsable_url,
                                          username=username)

            # http://blog.livedoor.jp/akusenkuto/shishikokuchi01.jpg
            case username, filename if cls.blog_img_pattern.match(filename):
                return ld.LivedoorImageUrl(parsed_url=parsable_url,
                                           username=username)

            case _:
                return None

    @staticmethod
    def _parse_aaa(parsable_url: ParsableUrl) -> ld.LivedoorUrl | UnsupportedUrl | None:
        match parsable_url.url_parts:
            # http://f49.aaa.livedoor.jp/~musashi/
            case username, if username.startswith("~"):
                return ld.LiveDoorAaaArtistUrl(parsed_url=parsable_url,
                                               username=username.removeprefix("~"),
                                               subdomain=parsable_url.subdomain)

            # http://f28.aaa.livedoor.jp/~inohuru/images/
            case username, "images" if username.startswith("~"):
                return ld.LiveDoorAaaArtistUrl(parsed_url=parsable_url,
                                               username=username.removeprefix("~"),
                                               subdomain=parsable_url.subdomain)

            # http://f20.aaa.livedoor.jp/%7Ekusaren/img/nk/2007new.jpg
            case username, "img", *_:
                return ld.LiveDoorAaaImageUrl(parsed_url=parsable_url,
                                              username=username.removeprefix("~"),
                                              subdomain=parsable_url.subdomain)

            # http://f20.aaa.livedoor.jp/%7Ekusaren/img/nk/2007new.jpg
            case username, "diary", filename if re.match(r"", filename):
                return ld.LiveDoorAaaImageUrl(parsed_url=parsable_url,
                                              username=username.removeprefix("~"),
                                              subdomain=parsable_url.subdomain)

            # http://f50.aaa.livedoor.jp/~holiday/asagayatei/
            case username, *_ if username.startswith("~"):
                return UnsupportedUrl(parsed_url=parsable_url)

            case _:
                return None
