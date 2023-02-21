from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.weibo import WeiboImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class SinaimgCnParser(UrlParser):
    SIZE_STRINGS = ["mw", "large", "orj", "middle", "original", "orignal"]
    # yeah, orignal http://s3.sinaimg.cn/orignal/7011f2d7hec2cafbb7dc2\u0026amp;690

    test_cases = {
        WeiboImageUrl: [
            "http://ww1.sinaimg.cn/large/69917555gw1f6ggdghk28j20c87lbhdt.jpg",
            "https://wx1.sinaimg.cn/large/002NQ2vhly1gqzqfk1agfj62981aw4qr02.jpg",
            "http://ww4.sinaimg.cn/mw690/77a2d531gw1f4u411ws3aj20m816fagg.jpg",
            "https://wx4.sinaimg.cn/orj360/e3930166gy1g546bz86cij20u00u040y.jpg",
            "http://ww3.sinaimg.cn/mw1024/0065kjmOgw1fabcanrzx6j30f00lcjwv.jpg",
            "https://wx1.sinaimg.cn/original/7004ec1cly1ge9dcbsw4lj20jg2ir7wh.jpg",
            "http://s2.sinaimg.cn/middle/645f3c7fg7715a2e3b711\u0026690",  # old
            "http://s3.sinaimg.cn/orignal/7011f2d7hec2cafbb7dc2\u0026amp;690",  # old
        ],
    }

    @ classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> WeiboImageUrl | None:
        match parsable_url.url_parts:

            case dimensions, _ if any(dimensions.startswith(string) for string in cls.SIZE_STRINGS):
                instance = WeiboImageUrl(parsable_url)

            case "m", "emoticon", *_:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance
