from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.sblo import SbloArticleUrl, SbloBlogUrl, SbloUrl
from danboorutools.models.url import UnsupportedUrl


class SbloJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> SbloUrl | None:
        match parsable_url.url_parts:
            # http://yuzu-soft.sblo.jp/
            case []:
                return SbloBlogUrl(parsed_url=parsable_url,
                                   blog_name=parsable_url.subdomain)

            # http://makkou.sblo.jp/article/186701561.html
            case "article", article_id:
                return SbloArticleUrl(parsed_url=parsable_url,
                                      blog_name=parsable_url.subdomain,
                                      article_id=int(article_id.removesuffix(".html")))

            # http://makkou.sblo.jp/s/article/186701561.html
            case "s", "article", article_id:
                return SbloArticleUrl(parsed_url=parsable_url,
                                      blog_name=parsable_url.subdomain,
                                      article_id=int(article_id.removesuffix(".html")))

            # http://morionohana.sblo.jp/s/
            case "s", :
                return SbloBlogUrl(parsed_url=parsable_url,
                                   blog_name=parsable_url.subdomain)

            case "archives", _archive_id:
                return UnsupportedUrl(parsed_url=parsable_url)

            # http://yuzu-soft.sblo.jp/category/583783-1.html
            case "category", _blog_category:
                return SbloBlogUrl(parsed_url=parsable_url,
                                   blog_name=parsable_url.subdomain)

            case _:
                return None
