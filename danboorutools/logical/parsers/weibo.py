from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.weibo import WeiboArtistUrl, WeiboImageUrl, WeiboPostUrl, WeiboUrl


class WeiboComParser(UrlParser):
    RESERVED_USERNAMES = ["u", "n", "p", "profile", "status", "detail"]
    domains = ("weibo.com", "weibo.cn")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> WeiboUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # http://tw.weibo.com/1300957955/3786333853668537
            # http://weibo.com/3357910224/EEHA1AyJP
            # https://www.weibo.com/5501756072/IF9fugHzj?from=page_1005055501756072_profile&wvr=6&mod=weibotime
            case artist_short_id, illust_base62_id if artist_short_id.isnumeric() and not illust_base62_id.islower():
                # dumb assumption, will bite me in the ass later
                return WeiboPostUrl(parsed_url=parsable_url,
                                    illust_base62_id=illust_base62_id,
                                    artist_short_id=int(artist_short_id))

            # http://photo.weibo.com/2125874520/wbphotos/large/mid/4194742441135220/pid/7eb64558gy1fnbryb5nzoj20dw10419t
            # http://photo.weibo.com/5732523783/talbum/detail/photo_id/4029784374069389?prel=p6_3
            case artist_short_id, _, _, _, illust_long_id, *_ if parsable_url.subdomain == "photo":
                return WeiboPostUrl(parsed_url=parsable_url, illust_long_id=int(
                    illust_long_id.split("#")[0]), artist_short_id=int(artist_short_id))

            # https://m.weibo.cn/detail/4506950043618873
            # https://www.weibo.com/detail/4676597657371957
            case "detail", illust_long_id:
                return WeiboPostUrl(parsed_url=parsable_url,
                                    illust_long_id=int(illust_long_id.split("#")[0]))

            # https://share.api.weibo.cn/share/304950356,4767694689143828.html
            # https://share.api.weibo.cn/share/304950356,4767694689143828
            case "share", stuff if parsable_url.subdomain == "share.api":
                return WeiboPostUrl(parsed_url=parsable_url,
                                    illust_long_id=int(stuff.split(",")[0]))

            # https://m.weibo.cn/status/J33G4tH1B
            case "status", illust_base62_id:
                return WeiboPostUrl(parsed_url=parsable_url,
                                    illust_base62_id=illust_base62_id)

            # https://www.weibo.com/u/5501756072
            # https://www.weibo.com/u/5957640693/home?wvr=5
            # https://m.weibo.cn/u/5501756072
            # https://m.weibo.cn/profile/5501756072
            case ("u" | "profile"), artist_short_id, *_:
                return WeiboArtistUrl(parsed_url=parsable_url,
                                      artist_short_id=int(artist_short_id))

            # https://www.weibo.com/p/1005055399876326 # https://www.weibo.com/u/5399876326, https://www.weibo.com/chengziyou666
            # https://www.weibo.com/p/1005055399876326/home?from=page_100505&mod=TAB&is_hot=1
            # https://www.weibo.cn/p/1005055399876326
            # https://m.weibo.com/p/1005055399876326
            case "p", artist_long_id, *_ if artist_long_id.isnumeric():
                return WeiboArtistUrl(parsed_url=parsable_url,
                                      artist_long_id=int(artist_long_id))

            # https://www.weibo.com/5501756072
            # https://www.weibo.cn/5501756072
            # https://weibo.com/1843267214/profile
            case artist_short_id, *_ if artist_short_id.isnumeric():
                return WeiboArtistUrl(parsed_url=parsable_url,
                                      artist_short_id=int(artist_short_id))

            # https://weibo.com/n/肆巳4
            # https://www.weibo.com/n/小小男爵不要坑
            case "n", screen_name, *_rest:
                return WeiboArtistUrl(parsed_url=parsable_url,
                                      screen_name=screen_name)

            case _, illust_long_id if parsable_url.subdomain == "tw" and illust_long_id.isnumeric():
                return WeiboPostUrl(parsed_url=parsable_url,
                                    illust_long_id=int(illust_long_id))

            # https://www.weibo.com/endlessnsmt # https://www.weibo.com/u/1879370780
            # https://www.weibo.cn/endlessnsmt
            # https://www.weibo.com/lvxiuzi0/home
            case username, *_ if username not in cls.RESERVED_USERNAMES:
                return WeiboArtistUrl(parsed_url=parsable_url,
                                      username=username)

            case "p", "searchall", *_:
                raise UnparsableUrlError(parsable_url)

            case _:
                return None


class SinaimgCnParser(UrlParser):
    SIZE_STRINGS = ("mw", "large", "orj", "middle", "original", "orignal")
    # yeah, "orignal" http://s3.sinaimg.cn/orignal/7011f2d7hec2cafbb7dc2\u0026amp;690

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> WeiboImageUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:

            # http://ww1.sinaimg.cn/large/69917555gw1f6ggdghk28j20c87lbhdt.jpg
            # https://wx1.sinaimg.cn/large/002NQ2vhly1gqzqfk1agfj62981aw4qr02.jpg
            # http://ww4.sinaimg.cn/mw690/77a2d531gw1f4u411ws3aj20m816fagg.jpg
            # https://wx4.sinaimg.cn/orj360/e3930166gy1g546bz86cij20u00u040y.jpg
            # http://ww3.sinaimg.cn/mw1024/0065kjmOgw1fabcanrzx6j30f00lcjwv.jpg
            # https://wx1.sinaimg.cn/original/7004ec1cly1ge9dcbsw4lj20jg2ir7wh.jpg
            # http://s2.sinaimg.cn/middle/645f3c7fg7715a2e3b711\u0026690
            # http://s3.sinaimg.cn/orignal/7011f2d7hec2cafbb7dc2\u0026amp;690
            case dimensions, _ if dimensions.startswith(cls.SIZE_STRINGS):
                return WeiboImageUrl(parsed_url=parsable_url)

            case "m", "emoticon", *_:
                raise UnparsableUrlError(parsable_url)

            case _:
                return None
