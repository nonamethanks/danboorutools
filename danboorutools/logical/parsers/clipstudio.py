from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.clipstudio import (
    ClipStudioAssetPostUrl,
    ClipStudioBlogUrl,
    ClipStudioProfileUrl,
    ClipStudioUrl,
    ClipStudioUserSearchUrl,
)
from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.models.url import UselessUrl


class ClipStudioParser(UrlParser):
    domains = ["clip-studio.com"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ClipStudioUrl | UselessUrl | None:
        instance: ClipStudioUrl | UselessUrl

        match parsable_url.url_parts:
            case _, "search":
                instance = ClipStudioUserSearchUrl(parsable_url)
                query = parsable_url.query.copy()
                query.pop("order", None)
                # https://assets.clip-studio.com/ja-jp/search?user=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8F&order=new
                # https://assets.clip-studio.com/ja-jp/search?user=隼人ろっく
                if list(query.keys()) == ["user"]:
                    instance.username = query["user"]
                # https://assets.clip-studio.com/ja-jp/search?word=へいたろう\u0026order=new
                elif list(query.keys()) == ["word"]:
                    return UselessUrl(parsable_url)
                else:
                    return None

            # https://profile.clip-studio.com/ja-jp/profile/cxhgegm-sc
            # https://profile.clip-studio.com/en-us/profile/gch9jit-cw
            case _, "profile", profile_id:
                instance = ClipStudioProfileUrl(parsable_url)
                instance.profile_id = profile_id

            # https://assets.clip-studio.com/ja-jp/detail?id=1946309
            case _, "detail" if parsable_url.subdomain == "assets":
                instance = ClipStudioAssetPostUrl(parsable_url)
                instance.asset_id = int(parsable_url.query["id"])

            # http://fuujin.sees.clip-studio.com/site/  # pretty sure these are all dead
            case _ if parsable_url.subdomain.endswith(".sees"):
                instance = ClipStudioBlogUrl(parsable_url)
                instance.blog_name = parsable_url.subdomain.removesuffix(".sees")

            # https://tech.clip-studio.com/howto/comicstudio/mayaaz
            case "howto", *_:
                raise UnparsableUrl(parsable_url)

            case "clip_site", *_:
                return UselessUrl(parsable_url)

            case _:
                return None

        return instance
