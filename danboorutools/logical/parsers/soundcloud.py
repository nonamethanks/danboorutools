from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.soundcloud import (
    SoundcloudArtistRedirectUrl,
    SoundcloudArtistUrl,
    SoundcloudPostSetUrl,
    SoundcloudPostUrl,
    SoundcloudUrl,
)
from danboorutools.models.url import UselessUrl


class SoundcloudComParser(UrlParser):
    RESERVED = ("signin", "feed", "home", "library", "upload", "contact", "pages", "imprint", "people",
                "terms-of-use", "download", "jobs", "creators", "blog", "developers", "hc", "artist", "checkout", "charts")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> SoundcloudUrl | UselessUrl | None:
        match parsable_url.url_parts:
            case redirect_id, if parsable_url.subdomain == "on":
                return SoundcloudArtistRedirectUrl(parsed_url=parsable_url,
                                                   redirect_id=redirect_id)

            case page, *_ if page in cls.RESERVED:
                return UselessUrl(parsed_url=parsable_url)

            # https://soundcloud.com/user-279939975/sets/7qi1o5xkayu5
            case username, "sets", post_id:
                return SoundcloudPostSetUrl(parsed_url=parsable_url,
                                            username=username,
                                            post_id=post_id)

            # https://soundcloud.com/kestbaile/baile-da-miku-ii-cadeia-paralela-astrophysics-dj-dengue
            case username, post_id:
                return SoundcloudPostUrl(parsed_url=parsable_url,
                                         username=username,
                                         post_id=post_id)

            # https://soundcloud.com/yonhlee
            case username, :
                return SoundcloudArtistUrl(parsed_url=parsable_url,
                                           username=username)

            case _:
                return None
