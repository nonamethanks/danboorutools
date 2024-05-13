from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.steamcommunity import SteamcommunityFileUrl, SteamCommunityProfileUrl
from danboorutools.models.url import UnsupportedUrl, Url, UselessUrl


class SteamcommunityComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> Url | None:
        match parsable_url.url_parts:
            # http://steamcommunity.com/id/sanmahurai
            case "id", username:
                return SteamCommunityProfileUrl(parsed_url=parsable_url,
                                                username=username)

            # http://steamcommunity.com/id/sanmahurai/myworkshopfiles/
            case "id", username, _:
                return SteamCommunityProfileUrl(parsed_url=parsable_url,
                                                username=username)

            # http://steamcommunity.com/profiles/76561198121582231
            case "profiles", user_id:
                return SteamCommunityProfileUrl(parsed_url=parsable_url,
                                                user_id=int(user_id))

            # http://steamcommunity.com/profiles/76561198121582231/myworkshopfiles
            case "profiles", user_id, _:
                return SteamCommunityProfileUrl(parsed_url=parsable_url,
                                                user_id=int(user_id))

            # http://steamcommunity.com/sharedfiles/filedetails/?id=663874840&amp;tscn=1467002725
            case "sharedfiles", "filedetails":
                return SteamcommunityFileUrl(parsed_url=parsable_url,
                                             file_id=int(parsable_url.query["id"]))

            case "groups", _group_name:
                return UnsupportedUrl(parsed_url=parsable_url)

            case ("app" | "games"), *_:
                return UnsupportedUrl(parsed_url=parsable_url)

            case "linkfilter", :
                query_url = parsable_url.query["u"].removeprefix("http://url=")
                return cls.parse(query_url)

            case "tradeoffer", *_:
                return UselessUrl(parsed_url=parsable_url)

            case _:
                return None
