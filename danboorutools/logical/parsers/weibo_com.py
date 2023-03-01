from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.weibo import WeiboArtistUrl, WeiboPostUrl, WeiboUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class WeiboComParser(UrlParser):
    RESERVED_USERNAMES = ["u", "n", "p", "profile", "status", "detail"]
    domains = ["weibo.com", "weibo.cn"]
    test_cases = {
        WeiboArtistUrl: [
            "https://www.weibo.com/u/5501756072",
            "https://www.weibo.com/u/5957640693/home?wvr=5",
            "https://m.weibo.cn/profile/5501756072",
            "https://m.weibo.cn/u/5501756072",
            "https://www.weibo.com/p/1005055399876326",  # https://www.weibo.com/u/5399876326, https://www.weibo.com/chengziyou666)
            "https://www.weibo.com/p/1005055399876326/home?from=page_100505&mod=TAB&is_hot=1",
            "https://www.weibo.cn/p/1005055399876326",
            "https://m.weibo.com/p/1005055399876326",
            "https://www.weibo.com/5501756072",
            "https://www.weibo.cn/5501756072",
            "https://weibo.com/1843267214/profile",
            "https://weibo.com/n/肆巳4",
            "https://www.weibo.com/n/小小男爵不要坑",
            "https://www.weibo.com/endlessnsmt",  # https://www.weibo.com/u/1879370780)
            "https://www.weibo.cn/endlessnsmt",
            "https://www.weibo.com/lvxiuzi0/home",
        ],
        WeiboPostUrl: [
            "http://tw.weibo.com/1300957955/3786333853668537",
            "http://weibo.com/3357910224/EEHA1AyJP",
            "https://www.weibo.com/5501756072/IF9fugHzj?from=page_1005055501756072_profile&wvr=6&mod=weibotime",
            "http://photo.weibo.com/2125874520/wbphotos/large/mid/4194742441135220/pid/7eb64558gy1fnbryb5nzoj20dw10419t",
            "http://photo.weibo.com/5732523783/talbum/detail/photo_id/4029784374069389?prel=p6_3",
            "https://m.weibo.cn/detail/4506950043618873",
            "https://www.weibo.com/detail/4676597657371957",

            "https://share.api.weibo.cn/share/304950356,4767694689143828.html",
            "https://share.api.weibo.cn/share/304950356,4767694689143828",
            "https://m.weibo.cn/status/J33G4tH1B",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> WeiboUrl | None:
        instance: WeiboUrl
        match parsable_url.url_parts:
            case artist_short_id, illust_base62_id if artist_short_id.isnumeric() and not illust_base62_id.islower():
                # dumb hack, will bite me in the ass later
                instance = WeiboPostUrl(parsable_url)
                instance.illust_base62_id = illust_base62_id
                instance.artist_short_id = int(artist_short_id)
            case artist_short_id, _, _, _, illust_long_id, *_ if parsable_url.subdomain == "photo":
                instance = WeiboPostUrl(parsable_url)
                instance.illust_long_id = int(illust_long_id.split("#")[0])
                instance.artist_short_id = int(artist_short_id)
            case "detail", illust_long_id:
                instance = WeiboPostUrl(parsable_url)
                instance.illust_long_id = int(illust_long_id.split("#")[0])
            case "share", stuff if parsable_url.subdomain == "share.api":
                instance = WeiboPostUrl(parsable_url)
                instance.illust_long_id = int(stuff.split(",")[0])
            case "status", illust_base62_id:
                instance = WeiboPostUrl(parsable_url)
                instance.illust_base62_id = illust_base62_id
            case ("u" | "profile"), artist_short_id, *_:
                instance = WeiboArtistUrl(parsable_url)
                instance.artist_short_id = int(artist_short_id)
            case "p", artist_long_id, *_ if artist_long_id.isnumeric():
                instance = WeiboArtistUrl(parsable_url)
                instance.artist_long_id = int(artist_long_id)
            case artist_short_id, *_ if artist_short_id.isnumeric():
                instance = WeiboArtistUrl(parsable_url)
                instance.artist_short_id = int(artist_short_id)
            case "n", display_name, *_rest:
                instance = WeiboArtistUrl(parsable_url)
                instance.display_name = display_name
            case _, illust_long_id if parsable_url.subdomain == "tw" and illust_long_id.isnumeric():
                instance = WeiboPostUrl(parsable_url)
                instance.illust_long_id = int(illust_long_id)
            case username, *_ if username not in cls.RESERVED_USERNAMES:
                instance = WeiboArtistUrl(parsable_url)
                instance.username = username

            case "p", "searchall", *_:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance
