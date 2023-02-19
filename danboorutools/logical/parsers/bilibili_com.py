from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.bilibili import (BilibiliArticleUrl, BilibiliArtistUrl, BilibiliLiveUrl, BilibiliPostUrl, BilibiliUrl,
                                                       BilibiliVideoUrl)
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class BilibiliComParser(UrlParser):
    domains = ["bilibili.com", "bilibili.tv"]

    test_cases = {
        BilibiliPostUrl: [
            "https://t.bilibili.com/686082748803186697",
            "https://t.bilibili.com/723052706467414039?spm_id_from=333.999.0.0",  # (quoted repost)
            "https://t.bilibili.com/h5/dynamic/detail/410234698927673781",

            "https://m.bilibili.com/dynamic/612214375070704555",
            "https://www.bilibili.com/opus/684571925561737250",
            "https://h.bilibili.com/83341894",

            "https://www.bilibili.com/p/h5/8773541",

        ],
        BilibiliArticleUrl: [
            "https://www.bilibili.com/read/cv7360489",
        ],
        BilibiliVideoUrl: [
            "https://www.bilibili.com/video/BV1dY4y1u7Vi/",
            "http://www.bilibili.tv/video/av439451/",
        ],
        BilibiliArtistUrl: [
            "https://space.bilibili.com/355143",
            "https://space.bilibili.com/476725595/dynamic",
            "https://space.bilibili.com/476725595/video",
            "http://www.bilibili.tv/member/index.php?mid=66804",
            "https://h.bilibili.com/member?mod=space%5Cu0026uid=4617101%5Cu0026act=p_index",
            "https://link.bilibili.com/p/world/index#/32122361/world/",
            "https://m.bilibili.com/space/489905",
            "http://space.bilibili.com/13574506#/album",
        ],
        BilibiliLiveUrl: [
            "https://live.bilibili.com/43602",
        ]
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> BilibiliUrl | None:
        instance: BilibiliUrl
        match parsable_url.url_parts:
            case user_id, *_ if parsable_url.subdomain == "space":
                instance = BilibiliArtistUrl(parsable_url)
                instance.user_id = int(user_id.strip("#"))

            case "space", user_id:
                instance = BilibiliArtistUrl(parsable_url)
                instance.user_id = int(user_id.strip("#"))

            case ("opus" | "dynamic"), post_id:
                instance = BilibiliPostUrl(parsable_url)
                instance.post_id = int(post_id)
                instance.post_type = "t"

            case "h5", "dynamic", "detail", post_id:
                instance = BilibiliPostUrl(parsable_url)
                instance.post_id = int(post_id)
                instance.post_type = "t"

            case "p", "h5", post_id:
                instance = BilibiliPostUrl(parsable_url)
                instance.post_id = int(post_id)
                instance.post_type = "h"

            case "read", article_id:
                instance = BilibiliArticleUrl(parsable_url)
                instance.article_id = int(article_id.removeprefix("cv"))

            case *_, "video", video_id:
                instance = BilibiliVideoUrl(parsable_url)
                instance.video_id = video_id

            case "member", "index.php":
                instance = BilibiliArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.params["mid"])

            case ["member"]:
                instance = BilibiliArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.params["uid"])

            case "p", "world", "index#", user_id, "world", *_:
                instance = BilibiliArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            case [post_id] if parsable_url.subdomain in ("t", "h"):
                instance = BilibiliPostUrl(parsable_url)
                try:
                    instance.post_id = int(post_id)
                except ValueError as e:
                    if post_id == "dy12125":
                        # https://danbooru.donmai.us/posts/1332451
                        raise UnparsableUrl(parsable_url) from e
                    else:
                        raise

                instance.post_type = parsable_url.subdomain  # type: ignore[assignment]

            case [live_id] if parsable_url.subdomain == "live":
                instance = BilibiliLiveUrl(parsable_url)
                instance.live_id = int(live_id)

            # http://www.bilibili.com/html/bizhi.html
            case "html", _:
                raise UnparsableUrl(parsable_url)

            # https://game.bilibili.com/sssj/#character
            case _ if parsable_url.subdomain == "game":
                raise UnparsableUrl(parsable_url)

            # https://live.bilibili.com/activity/qixi-festival-2020-pc/index.html#/battle
            # https://www.bilibili.com/festival/arknights2022?bvid=BV1sr4y1e7gQ
            case ("activity" | "festival"), *_:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance
