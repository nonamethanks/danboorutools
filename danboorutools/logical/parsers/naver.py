from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.naver import NaverBlogArtistUrl, NaverBlogPostUrl, NaverCafeArtistUrl, NaverCafePostUrl, NaverUrl


class NaverComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> NaverUrl | None:
        if parsable_url.subdomain == "cafe":
            return cls._match_cafe(parsable_url)
        elif parsable_url.subdomain == "blog":
            return cls._match_blog(parsable_url)
        else:
            return None

    @staticmethod
    def _match_cafe(parsable_url: ParsableUrl) -> NaverUrl | None:
        instance: NaverUrl

        match parsable_url.url_parts:
            case username, post_id:
                instance = NaverCafePostUrl(parsable_url)
                instance.username = username
                instance.post_id = int(post_id)
            case username, :
                instance = NaverCafeArtistUrl(parsable_url)
                instance.username = username
            case _:
                return None
        return instance

    @staticmethod
    def _match_blog(parsable_url: ParsableUrl) -> NaverUrl | None:
        instance: NaverUrl

        match parsable_url.url_parts:
            case username, post_id:
                instance = NaverBlogPostUrl(parsable_url)
                instance.username = username
                instance.post_id = int(post_id)
            case username, :
                instance = NaverBlogArtistUrl(parsable_url)
                instance.username = username
            case _:
                return None
        return instance
