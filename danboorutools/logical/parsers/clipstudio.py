from danboorutools.logical.extractors.clipstudio import ClipStudioAssetPostUrl, ClipStudioProfileUrl, ClipStudioUrl, ClipStudioUserSearchUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class ClipStudioParser(UrlParser):
    domains = ["clip-studio.com"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ClipStudioUrl | None:
        instance: ClipStudioUrl

        match parsable_url.url_parts:
            # https://assets.clip-studio.com/ja-jp/search?user=%E9%9A%BC%E4%BA%BA%E3%82%8D%E3%81%A3%E3%81%8F&order=new
            case "ja-jp", "search":
                instance = ClipStudioUserSearchUrl(parsable_url)
                instance.username = parsable_url.query["user"]

            # https://profile.clip-studio.com/ja-jp/profile/cxhgegm-sc
            case "ja-jp", "profile", profile_id:
                instance = ClipStudioProfileUrl(parsable_url)
                instance.profile_id = profile_id

            # https://assets.clip-studio.com/ja-jp/detail?id=1946309
            case "ja-jp", "detail" if parsable_url.subdomain == "assets":
                instance = ClipStudioAssetPostUrl(parsable_url)
                instance.asset_id = int(parsable_url.query["id"])

            case _:
                return None

        return instance
