from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import bilibili as b


class BilibiliComParser(UrlParser):
    domains = ("bilibili.com", "bilibili.tv")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> b.BilibiliUrl | None:
        instance: b.BilibiliUrl
        match parsable_url.url_parts:

            # https://space.bilibili.com/355143
            # https://space.bilibili.com/476725595/dynamic
            # https://space.bilibili.com/476725595/video
            # http://space.bilibili.com/13574506#/album
            case user_id, *_ if parsable_url.subdomain == "space":
                return b.BilibiliArtistUrl(parsed_url=parsable_url,
                                           user_id=int(user_id.strip("#")))

            # https://m.bilibili.com/space/489905
            case "space", user_id:
                return b.BilibiliArtistUrl(parsed_url=parsable_url,
                                           user_id=int(user_id.strip("#")))

            # https://m.bilibili.com/dynamic/612214375070704555
            # https://www.bilibili.com/opus/684571925561737250
            case ("opus" | "dynamic"), post_id:
                return b.BilibiliPostUrl(parsed_url=parsable_url,
                                         post_id=int(post_id),
                                         post_type="t")

            # https://t.bilibili.com/h5/dynamic/detail/410234698927673781
            case "h5", "dynamic", "detail", post_id:
                return b.BilibiliPostUrl(parsed_url=parsable_url,
                                         post_id=int(post_id),
                                         post_type="t")

            # https://www.bilibili.com/p/h5/8773541
            case "p", "h5", post_id:
                return b.BilibiliPostUrl(parsed_url=parsable_url,
                                         post_id=int(post_id),
                                         post_type="h")

            # https://www.bilibili.com/read/cv7360489
            case "read", article_id:
                return b.BilibiliArticleUrl(parsed_url=parsable_url,
                                            article_id=int(article_id.removeprefix("cv")))

            # https://www.bilibili.com/video/BV1dY4y1u7Vi/
            # http://www.bilibili.tv/video/av439451/
            case *_, "video", video_id:
                return b.BilibiliVideoPostUrl(parsed_url=parsable_url,
                                              video_id=video_id)

            # http://www.bilibili.tv/member/index.php?mid=66804
            case "member", "index.php":
                return b.BilibiliArtistUrl(parsed_url=parsable_url,
                                           user_id=int(parsable_url.query["mid"]))

            # https://h.bilibili.com/member?mod=space%5Cu0026uid=4617101%5Cu0026act=p_index
            case "member", :
                return b.BilibiliArtistUrl(parsed_url=parsable_url,
                                           user_id=int(parsable_url.query["uid"]))

            # https://link.bilibili.com/p/world/index#/32122361/world/
            case "p", "world", "index#", user_id, "world", *_:
                return b.BilibiliArtistUrl(parsed_url=parsable_url,
                                           user_id=int(user_id))

            # https://t.bilibili.com/686082748803186697
            # https://t.bilibili.com/723052706467414039?spm_id_from=333.999.0.0 (quoted repo)
            # https://h.bilibili.com/83341894
            case post_id, if parsable_url.subdomain in ("t", "h"):
                try:
                    post_id_int = int(post_id)
                except ValueError as e:
                    if post_id == "dy12125":
                        # https://danbooru.donmai.us/posts/1332451
                        raise UnparsableUrlError(parsable_url) from e
                    raise

                instance = b.BilibiliPostUrl(parsed_url=parsable_url,
                                             post_id=post_id_int,
                                             post_type=parsable_url.subdomain)  # type: ignore[arg-type]

            # https://live.bilibili.com/43602
            case live_id, if parsable_url.subdomain == "live":
                return b.BilibiliLiveUrl(parsed_url=parsable_url,
                                         live_id=int(live_id))

            # http://www.bilibili.com/html/bizhi.html
            case "html", _:
                raise UnparsableUrlError(parsable_url)

            # https://game.bilibili.com/sssj/#character
            case _ if parsable_url.subdomain == "game":
                raise UnparsableUrlError(parsable_url)

            # https://live.bilibili.com/activity/qixi-festival-2020-pc/index.html#/battle
            # https://www.bilibili.com/festival/arknights2022?bvid=BV1sr4y1e7gQ
            case ("activity" | "festival"), *_:
                raise UnparsableUrlError(parsable_url)

            case _:
                return None

        return instance


class HdslbComParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> b.BilibiliImageUrl | None:
        match parsable_url.url_parts:

            # https://i0.hdslb.com/bfs/new_dyn/675526fd8baa2f75d7ea0e7ea957bc0811742550.jpg@1036w.webp
            # https://i0.hdslb.com/bfs/new_dyn/716a9733fc804d11d823cfacb7a3c78b11742550.jpg@208w_208h_1e_1c.webp
            # https://i0.hdslb.com/bfs/new_dyn/bb4e6e265174f53672ba9c87fcf23f0f468367.jpg TODO: fix this on danbooru code too: not 8 digits
            case "bfs", "new_dyn", _filename:
                return b.BilibiliImageUrl(parsed_url=parsable_url,
                                          user_id=parsable_url.stem)

            # https://i0.hdslb.com/bfs/album/37f77871d417c76a08a9467527e9670810c4c442.gif@1036w.webp
            # https://i0.hdslb.com/bfs/album/37f77871d417c76a08a9467527e9670810c4c442.gif
            # https://i0.hdslb.com/bfs/article/48e75b3871fa5ed62b4e3a16bf60f52f96b1b3b1.jpg@942w_1334h_progressive.webp
            case "bfs", ("album" | "article"), _:
                return b.BilibiliImageUrl(parsed_url=parsable_url,
                                          user_id=None)

            #  http://i1.hdslb.com/bfs/archive/89bfa8427528a5e45eff457d4af3a59a9d3f54e0.jpg
            # http://i0.hdslb.com/bfs/common_activity/3bc320c168494f5b7d3daa29927cfb23.jpg
            case "bfs", ("archive" | "common_activity"), _:
                raise UnparsableUrlError(parsable_url)  # 404 images I think?

            # https://i0.hdslb.com/bfs/activity-plat/static/2cf2b9af5d3c5781d611d6e36f405144/E738vcDvd3.png
            case "bfs", "activity-plat", _, _, _:
                raise UnparsableUrlError(parsable_url)  # 404 images I think?

            # https://i0.hdslb.com/u_user/879a1e5ac43748c4c27ccbb2cb3497f7.png
            # http://i0.hdslb.com/Wallpaper/summer_2011_wide.jpg
            # http://i1.hdslb.com/u_user/Wallpaper/bilibili_5th.png
            case *_, ("u_user" | "Wallpaper"), _:
                raise UnparsableUrlError(parsable_url)  # 404 images I think?

            case _:
                return None
