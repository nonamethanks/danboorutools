import re

from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.geocities import GeocitiesBlogUrl, GeocitiesImageUrl, GeocitiesPageUrl, GeocitiesUrl


class GeocitiesParser(UrlParser):
    domains = ("geocities.jp", "geocities.com")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> GeocitiesUrl | None:
        match parsable_url.url_parts:

            case blog_name, :
                return GeocitiesBlogUrl(parsed_url=parsable_url, blog_name=blog_name, tld=parsable_url.tld)

            case blog_name, *path:
                final_path = path[-1].lower().strip("#")
                if final_path.endswith((".html", ".htm")):
                    return GeocitiesPageUrl(parsed_url=parsable_url,
                                            blog_name=blog_name,
                                            tld=parsable_url.tld)

                elif final_path.endswith((".png", ".gif", ".jpg", ".jpeg", ".swf")):
                    return GeocitiesImageUrl(parsed_url=parsable_url,
                                             blog_name=blog_name,
                                             tld=parsable_url.tld)

                elif not re.match(r".*\.\w{3,}.$", final_path):
                    return GeocitiesPageUrl(parsed_url=parsable_url,
                                            blog_name=blog_name,
                                            tld=parsable_url.tld)

                else:
                    return None

            case _:
                return None
