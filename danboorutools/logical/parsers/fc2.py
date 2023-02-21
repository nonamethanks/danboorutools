from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.fc2 import Fc2BlogUrl, Fc2ImageUrl, Fc2PiyoBlogUrl, Fc2PiyoPostUrl, Fc2PostUrl, Fc2Url
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class Fc2Parser(UrlParser):
    domains = ["fc2.com", "fc2blog.net", "fc2blog.us", "2nt.com"]
    UNPARSED_SUBSITES = (
        "bbs1",
        "bbs10",            # http://bbs10.fc2.com//bbs/img/_184700/184628/full/184628_1307192498.jpg
        "cart1",            # http://cart1.fc2.com/user_img/c/core/3_2_09.jpg
        "clap",             # http://clap.fc2.com/uploads/r/u/rukahi/w_naoto09clap.jpg
        "creator",          # http://creator.fc2.com/files/2/0/5/0502/
        "deep",             # http://www.deep.fc2.com/0g0reiTpd.JPG
        "finito",           # https://izen.finito.fc2.com/
        "form",
        "form1",            # http://form1.fc2.com/form/?id=518534
        "form1ssl",
        "k2",               # https://k2.fc2.com/cgi-bin/hp.cgi/manoji_honpo/
        "live",             # http://live.fc2.com/85105083
        "livechat",         # http://livechat.fc2.com/29801826/
        "novel",
        "pimp",             # https://ashi.pimp.fc2.com/
        "pr",               # http://pr.fc2.com/tukimine/
        "summary-cdn",
        "summary-img-cdn",  # https://summary-img-cdn.fc2.com/summaryfc2/img/summary/widget/251929.jpeg
        "video",            # http://video.fc2.com/content/20120513ycqgGPhn/
        "wiki",             # https://ronico.wiki.fc2.com/wiki/%E5%86%A0%E6%9C%88%E3%83%A6%E3%82%A6
    )

    test_cases = {
        Fc2BlogUrl: [
            "http://silencexs.blog.fc2.com",
            "http://silencexs.blog106.fc2.com",
            "http://chika108.blog.2nt.com",

            "http://794ancientkyoto.web.fc2.com",
            "http://yorokobi.x.fc2.com",
            "https://lilish28.bbs.fc2.com",
            "http://jpmaid.h.fc2.com",

            "http://toritokaizoku.web.fc2.com/tori.html",

            "http://swordsouls.blog131.fc2blog.net",
            "http://swordsouls.blog131.fc2blog.us",
            "http://diary.fc2.com/cgi-sys/ed.cgi/kazuharoom/?Y=2012&M=10&D=22",

            "http://ojimahonpo.web.fc2.com/site/",
            "http://ramepan.web.fc2.com/pict/",
            "http://celis.x.fc2.com/gallery/dai3_2/dai3_2.htm",
            "http://seimen10.h.fc2.com/top.htm",

            "http://blog-imgs-32.fc2.com/e/r/o/erosanimest/",
            "https://usagigoyakikaku.cart.fc2.com/?preview=31plzD8O7SP3",

            "http://blog36.fc2.com/acidhead",

            "http://tororohanrok.blog111.fc2.com/category7-1",

            "http://blog.fc2.com/m/mosha2/",

        ],
        Fc2ImageUrl: [
            "http://onidocoro.blog14.fc2.com/file/20071003061150.png",
            "http://blog23.fc2.com/m/mosha2/file/uru.jpg",
            "http://blog.fc2.com/g/genshi/file/20070612a.jpg",

            "http://blog-imgs-63-origin.fc2.com/y/u/u/yuukyuukikansya/140817hijiri02.jpg",
            "http://blog-imgs-61.fc2.com/o/m/o/omochi6262/20130402080220583.jpg",
            "http://blog.fc2.com/g/b/o/gbot/20071023195141.jpg",


            "http://diary.fc2.com/user/yuuri/img/2005_12/26.jpg",
            "http://diary1.fc2.com/user/kou_48/img/2006_8/14.jpg",
            "http://diary.fc2.com/user/kazuharoom/img/2015_5/22.jpg",
            "http://doskoinpo.blog133.fc2.com/?mode=image&filename=SIBARI03.jpg",
            "http://doskoinpo.blog133.fc2.com/img/SIBARI03.jpg/",
            "https://blog-imgs-19.fc2.com/5/v//5v/yukkuri0.jpg",
            "http://shohomuga.blog83.fc2.com/20071014181747.jpg",
            "https://blog-imgs-145-origin.2nt.com/k/a/t/katourennyuu/210626_0003.jpg"
        ],
        Fc2PostUrl: [
            "http://hosystem.blog36.fc2.com/blog-entry-37.html",
            "http://kozueakari02.blog.2nt.com/blog-entry-115.html",
        ],
        Fc2PiyoPostUrl: [
            "https://piyo.fc2.com/omusubi/26890/",
        ],
        Fc2PiyoBlogUrl: [
            "https://piyo.fc2.com/omusubi/start/5/",
        ]

    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Fc2Url | None:
        if "." in parsable_url.subdomain:
            username, subsite = parsable_url.subdomain.rsplit(".", maxsplit=1)
        else:
            subsite = parsable_url.subdomain
            username = None

        if subsite.startswith("blog") and username:
            instance = cls._match_blog_username_in_subdomain(parsable_url)
            if instance:
                instance.username = username
        elif subsite.startswith("blog"):
            instance = cls._match_blog_only_subdomain(parsable_url)
        elif subsite.startswith("diary"):
            instance = cls._match_diary(parsable_url)
        elif subsite in ("x", "h", "web", "bbs", "kt", "cart", "sns") and username:
            instance = Fc2BlogUrl(parsable_url)
            instance.username = username
        elif subsite == "piyo":
            instance = cls._match_piyo(parsable_url)
        elif subsite in cls.UNPARSED_SUBSITES:
            # TODO: investigate whether it's all bad_id. Same for x/h/web/etc
            # also I ain't parsing novel.fc2.com
            raise UnparsableUrl(parsable_url)
        else:
            instance = None

        if not instance:
            return None

        instance.subsite = subsite
        return instance

    @staticmethod
    def _match_blog_only_subdomain(parsable_url: ParsableUrl) -> Fc2Url | None:
        instance: Fc2Url
        match parsable_url.url_parts:
            case char, username, "file", _ if len(char) == 1:
                instance = Fc2ImageUrl(parsable_url)

            case char, username if len(char) == 1:
                instance = Fc2BlogUrl(parsable_url)

            case char1, char2, char3, username, _ if all(len(char) == 1 for char in [char1, char2, char3]):
                instance = Fc2ImageUrl(parsable_url)

            case char1, char2, char3, username if all(len(char) == 1 for char in [char1, char2, char3]):
                instance = Fc2BlogUrl(parsable_url)

            # https://blog-imgs-19.fc2.com/5/v//5v/yukkuri0.jpg
            case char1, char2, username, _, if len(username) == 2 and all(len(char) == 1 for char in [char1, char2]):
                instance = Fc2ImageUrl(parsable_url)

            case [username]:
                instance = Fc2BlogUrl(parsable_url)

            case _:
                return None

        instance.username = username
        return instance

    @staticmethod
    def _match_diary(parsable_url: ParsableUrl) -> Fc2Url | None:
        instance: Fc2Url
        match parsable_url.url_parts:
            case "user", username, "img", *_:
                instance = Fc2ImageUrl(parsable_url)

            case "user", username:
                instance = Fc2BlogUrl(parsable_url)

            case "cgi-sys", "ed.cgi", username:
                instance = Fc2BlogUrl(parsable_url)

            case _:
                return None

        instance.username = username
        return instance

    @staticmethod
    def _match_blog_username_in_subdomain(parsable_url: ParsableUrl) -> Fc2Url | None:
        instance: Fc2Url
        match parsable_url.url_parts:
            case [] if parsable_url.params:
                instance = Fc2ImageUrl(parsable_url)

            case []:
                instance = Fc2BlogUrl(parsable_url)

            case [blog_entry] if blog_entry.startswith("blog-entry-"):
                instance = Fc2PostUrl(parsable_url)
                instance.post_id = int(blog_entry.split(".")[0].split("-")[-1])

            case [html_page] if html_page.endswith(".html"):
                instance = Fc2BlogUrl(parsable_url)

            case "file", _:
                instance = Fc2ImageUrl(parsable_url)

            case "img", _:
                instance = Fc2ImageUrl(parsable_url)

            case "tb.php", _:
                # http://aenmix.blog93.fc2.com/tb.php/46-e4374dd5
                raise UnparsableUrl(parsable_url)

            case [page] if page.startswith("category"):
                instance = Fc2BlogUrl(parsable_url)

            case [page] if any(page.endswith(ext) for ext in [".jpg", "png", "gif"]):
                instance = Fc2ImageUrl(parsable_url)

            case _:
                return None

        return instance

    @staticmethod
    def _match_piyo(parsable_url: ParsableUrl) -> Fc2Url | None:
        instance: Fc2Url
        match parsable_url.url_parts:
            case username, post_id if post_id.isnumeric():
                instance = Fc2PiyoPostUrl(parsable_url)
                instance.post_id = int(post_id)
            case username, *_:
                instance = Fc2PiyoBlogUrl(parsable_url)
            case _:
                return None

        instance.username = username
        return instance
