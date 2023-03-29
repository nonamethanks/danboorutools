from functools import lru_cache
from urllib.parse import urlencode

from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import fc2
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

    @lru_cache
    @staticmethod
    def username_and_subsite_from_subdomain(subdomain: str) -> tuple[str, str | None]:
        if "." in subdomain:
            username, _, subsite = subdomain.rpartition(".")
        else:
            subsite = subdomain
            username = None
        return subsite, username

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> fc2.Fc2Url | UnsupportedUrl | None:
        subsite, username = cls.username_and_subsite_from_subdomain(parsable_url.subdomain)
        if subsite.startswith("blog") and username:
            return cls._match_blog_username_in_subdomain(parsable_url, username)
        elif subsite.startswith("blog"):
            return cls._match_blog_only_subdomain(parsable_url)
        elif subsite.startswith("diary"):
            return cls._match_diary(parsable_url)
        elif subsite in ("x", "h", "web", "bbs", "kt", "cart", "sns") and username:
            return fc2.Fc2BlogUrl(parsed_url=parsable_url,
                                  username=username,
                                  subsite=subsite,
                                  domain=parsable_url.domain)
        elif subsite == "piyo":
            return cls._match_piyo(parsable_url)
        elif subsite in cls.UNPARSED_SUBSITES:
            # TODO: investigate whether it's all bad_id. Same for x/h/web/etc
            # also I ain't parsing novel.fc2.com
            return UnsupportedUrl(parsed_url=parsable_url)
        else:
            return None

    @staticmethod
    # type: ignore[return]
    def _match_blog_username_in_subdomain(parsable_url: ParsableUrl, username: str) -> fc2.Fc2Url | None:
        match parsable_url.url_parts:
            case [] if parsable_url.query:
                return fc2.Fc2ImageUrl(parsed_url=parsable_url,
                                       subsite="blog",
                                       username=username)

            case []:
                return fc2.Fc2BlogUrl(parsed_url=parsable_url,
                                      subsite="blog",
                                      username=username,
                                      domain=parsable_url.domain)

            case blog_entry, if blog_entry.startswith("blog-entry-"):
                post_id = int(parsable_url.stem.split("-")[-1])
                return fc2.Fc2PostUrl(parsed_url=parsable_url,
                                      subsite="blog",
                                      username=username,
                                      domain=parsable_url.domain,
                                      post_id=post_id)

            case html_page, if html_page.endswith(".html"):
                return fc2.Fc2BlogUrl(parsed_url=parsable_url,
                                      subsite="blog",
                                      username=username,
                                      domain=parsable_url.domain)

            case "file", _:
                return fc2.Fc2ImageUrl(parsed_url=parsable_url,
                                       subsite="blog",
                                       username=username)

            case "img", _:
                return fc2.Fc2ImageUrl(parsed_url=parsable_url,
                                       subsite="blog",
                                       username=username)

            case "tb.php", _:
                # http://aenmix.blog93.fc2.com/tb.php/46-e4374dd5
                raise UnparsableUrlError(parsable_url)

            case page, if page.startswith("category"):
                return fc2.Fc2BlogUrl(parsed_url=parsable_url,
                                      username=username,
                                      subsite="blog",
                                      domain=parsable_url.domain)

            case page, if any(page.endswith(ext) for ext in [".jpg", "png", "gif"]):
                return fc2.Fc2ImageUrl(parsed_url=parsable_url,
                                       subsite="blog",
                                       username=username)

            case _:
                return None

    @classmethod
    def _match_blog_only_subdomain(cls, parsable_url: ParsableUrl) -> fc2.Fc2Url | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case char, username, "file", _ if len(char) == 1:
                return fc2.Fc2ImageUrl(parsed_url=parsable_url,
                                       subsite="blog",
                                       username=username)

            case char, username if len(char) == 1:
                return fc2.Fc2BlogUrl(parsed_url=parsable_url,
                                      subsite="blog",
                                      username=username,
                                      domain=parsable_url.domain)

            case char1, char2, char3, username, _ if all(len(char) == 1 for char in [char1, char2, char3]):
                return fc2.Fc2ImageUrl(parsed_url=parsable_url,
                                       subsite="blog",
                                       username=username)

            case char1, char2, char3, username if all(len(char) == 1 for char in [char1, char2, char3]):
                return fc2.Fc2BlogUrl(parsed_url=parsable_url,
                                      subsite="blog",
                                      username=username,
                                      domain=parsable_url.domain)

            # https://blog-imgs-19.fc2.com/5/v//5v/yukkuri0.jpg
            case char1, char2, username, _, if len(username) == 2 and all(len(char) == 1 for char in [char1, char2]):
                return fc2.Fc2ImageUrl(parsed_url=parsable_url,
                                       subsite="blog",
                                       username=username)

            case username, :
                return fc2.Fc2BlogUrl(parsed_url=parsable_url,
                                      subsite="blog",
                                      username=username,
                                      domain=parsable_url.domain)

            case _:
                return None

    @staticmethod
    def _match_diary(parsable_url: ParsableUrl) -> fc2.Fc2Url | None:
        match parsable_url.url_parts:
            case "user", username, "img", *_:
                return fc2.Fc2ImageUrl(parsed_url=parsable_url,
                                       username=username,
                                       subsite="diary")

            case "user", username:
                if "Y" in parsable_url.query and "M" in parsable_url.query:
                    return fc2.Fc2DiaryPostUrl(parsed_url=parsable_url,
                                               post_date_string=urlencode(parsable_url.query),
                                               username=username)
                else:
                    return fc2.Fc2DiaryArtistUrl(parsed_url=parsable_url,
                                                 username=username)

            case "cgi-sys", "ed.cgi", username:
                if "Y" in parsable_url.query and "M" in parsable_url.query:
                    return fc2.Fc2DiaryPostUrl(parsed_url=parsable_url,
                                               post_date_string=urlencode(parsable_url.query),
                                               username=username)
                else:
                    return fc2.Fc2DiaryArtistUrl(parsed_url=parsable_url,
                                                 username=username)

            case _:
                return None

    @staticmethod
    def _match_piyo(parsable_url: ParsableUrl) -> fc2.Fc2Url | None:  # type: ignore[return]
        match parsable_url.url_parts:
            case username, post_id if post_id.isnumeric():
                return fc2.Fc2PiyoPostUrl(parsed_url=parsable_url,
                                          username=username,
                                          post_id=int(post_id))
            case username, *_:
                return fc2.Fc2PiyoBlogUrl(parsed_url=parsable_url,
                                          username=username)
            case _:
                return None
