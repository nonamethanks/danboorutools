from urllib.parse import urlencode

from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.extractors import fc2
from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.models.url import UnsupportedUrl


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

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> fc2.Fc2Url | UnsupportedUrl | None:
        if "." in parsable_url.subdomain:
            username, _, subsite = parsable_url.subdomain.rpartition(".")
        else:
            subsite = parsable_url.subdomain
            username = None

        if subsite.startswith("blog") and username:
            instance = cls._match_blog_username_in_subdomain(parsable_url)
            if instance:
                instance.username = username
            subsite = "blog"
        elif subsite.startswith("blog"):
            instance = cls._match_blog_only_subdomain(parsable_url)
            subsite = "blog"
        elif subsite.startswith("diary"):
            instance = cls._match_diary(parsable_url)
            subsite = "diary"
        elif subsite in ("x", "h", "web", "bbs", "kt", "cart", "sns") and username:
            instance = fc2.Fc2BlogUrl(parsable_url)
            instance.username = username
        elif subsite == "piyo":
            instance = cls._match_piyo(parsable_url)
        elif subsite in cls.UNPARSED_SUBSITES:
            # TODO: investigate whether it's all bad_id. Same for x/h/web/etc
            # also I ain't parsing novel.fc2.com
            return UnsupportedUrl(parsable_url)
        else:
            instance = None

        if not instance:
            return None

        instance.subsite = subsite
        instance.domain = parsable_url.domain
        return instance

    @staticmethod
    def _match_blog_only_subdomain(parsable_url: ParsableUrl) -> fc2.Fc2Url | None:
        instance: fc2.Fc2Url
        match parsable_url.url_parts:
            case char, username, "file", _ if len(char) == 1:
                instance = fc2.Fc2ImageUrl(parsable_url)

            case char, username if len(char) == 1:
                instance = fc2.Fc2BlogUrl(parsable_url)

            case char1, char2, char3, username, _ if all(len(char) == 1 for char in [char1, char2, char3]):
                instance = fc2.Fc2ImageUrl(parsable_url)

            case char1, char2, char3, username if all(len(char) == 1 for char in [char1, char2, char3]):
                instance = fc2.Fc2BlogUrl(parsable_url)

            # https://blog-imgs-19.fc2.com/5/v//5v/yukkuri0.jpg
            case char1, char2, username, _, if len(username) == 2 and all(len(char) == 1 for char in [char1, char2]):
                instance = fc2.Fc2ImageUrl(parsable_url)

            case username, :
                instance = fc2.Fc2BlogUrl(parsable_url)

            case _:
                return None

        instance.username = username
        return instance

    @staticmethod
    def _match_diary(parsable_url: ParsableUrl) -> fc2.Fc2Url | None:
        instance: fc2.Fc2Url
        match parsable_url.url_parts:
            case "user", username, "img", *_:
                instance = fc2.Fc2ImageUrl(parsable_url)

            case "user", username:
                if "Y" in parsable_url.query and "M" in parsable_url.query:
                    instance = fc2.Fc2DiaryPostUrl(parsable_url)
                    instance.post_date_string = urlencode(parsable_url.query)
                else:
                    instance = fc2.Fc2DiaryArtistUrl(parsable_url)

            case "cgi-sys", "ed.cgi", username:
                if "Y" in parsable_url.query and "M" in parsable_url.query:
                    instance = fc2.Fc2DiaryPostUrl(parsable_url)
                    instance.post_date_string = urlencode(parsable_url.query)
                else:
                    instance = fc2.Fc2DiaryArtistUrl(parsable_url)

            case _:
                return None

        instance.username = username
        return instance

    @staticmethod
    def _match_blog_username_in_subdomain(parsable_url: ParsableUrl) -> fc2.Fc2Url | None:
        instance: fc2.Fc2Url
        match parsable_url.url_parts:
            case [] if parsable_url.query:
                instance = fc2.Fc2ImageUrl(parsable_url)

            case []:
                instance = fc2.Fc2BlogUrl(parsable_url)

            case blog_entry, if blog_entry.startswith("blog-entry-"):
                instance = fc2.Fc2PostUrl(parsable_url)
                instance.post_id = int(parsable_url.stem.split("-")[-1])

            case html_page, if html_page.endswith(".html"):
                instance = fc2.Fc2BlogUrl(parsable_url)

            case "file", _:
                instance = fc2.Fc2ImageUrl(parsable_url)

            case "img", _:
                instance = fc2.Fc2ImageUrl(parsable_url)

            case "tb.php", _:
                # http://aenmix.blog93.fc2.com/tb.php/46-e4374dd5
                raise UnparsableUrlError(parsable_url)

            case page, if page.startswith("category"):
                instance = fc2.Fc2BlogUrl(parsable_url)

            case page, if any(page.endswith(ext) for ext in [".jpg", "png", "gif"]):
                instance = fc2.Fc2ImageUrl(parsable_url)

            case _:
                return None

        return instance

    @staticmethod
    def _match_piyo(parsable_url: ParsableUrl) -> fc2.Fc2Url | None:
        instance: fc2.Fc2Url
        match parsable_url.url_parts:
            case username, post_id if post_id.isnumeric():
                instance = fc2.Fc2PiyoPostUrl(parsable_url)
                instance.post_id = int(post_id)
                instance.username = username
            case username, *_:
                instance = fc2.Fc2PiyoBlogUrl(parsable_url)
            case _:
                return None

        instance.username = username
        return instance
