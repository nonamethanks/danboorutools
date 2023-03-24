import re

from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.sakura import SakuraBlogUrl, SakuraUrl


class SakuraNeJpParser(UrlParser):
    domains = ["sakura.ne.jp", "x0.com"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> SakuraUrl | None:
        blog_name = parsable_url.subdomain
        if "." in blog_name:
            _, blog_name = re.split(r"www\d*.", parsable_url.subdomain)
        assert blog_name

        instance = SakuraBlogUrl(parsable_url)

        instance.blog_name = blog_name
        return instance
