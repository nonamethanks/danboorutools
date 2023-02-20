import re

from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors import fanbox as f
from danboorutools.logical.extractors import pixiv as p
from danboorutools.logical.extractors import pixiv_comic as c
from danboorutools.logical.extractors import pixiv_sketch as s
from danboorutools.logical.parsers import ParsableUrl, UrlParser

img_subdomain_pattern = re.compile(r"^i(?:mg)?\d*$")


class PixivNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> p.PixivUrl | s.PixivSketchUrl | c.PixivComicUrl | f.FanboxUrl | None:
        if img_subdomain_pattern.match(parsable_url.subdomain):
            return cls._match_i_subdomain(parsable_url)
        if parsable_url.url_parts[0] == "fanbox":
            return cls._match_fanbox_path(parsable_url)
        if parsable_url.subdomain in ("www", ""):
            return cls._match_no_subdomain(parsable_url)
        elif parsable_url.subdomain in ("sketch", "img-sketch"):
            return cls._match_sketch_subdomain(parsable_url)
        elif parsable_url.subdomain == "fanbox":
            return cls._match_fanbox_subdomain(parsable_url)
        elif parsable_url.subdomain == "comic":
            return cls._match_comic_subdomain(parsable_url)
        elif parsable_url.subdomain == "blog":
            instance = p.PixivStaccUrl(parsable_url)
            instance.stacc = parsable_url.url_parts[0]
            return instance
        # https://sensei.pixiv.net/ja/course/30
        # http://imgaz.pixiv.net/img_group/200/1024091/d0928738938a2c8ecba3dd3a57a4c2ad.png
        # https://source.pixiv.net/source/images/contest/050plus-fes.jpg
        # http://dev.pixiv.net/img/event/princessroyale/8.png
        # http://chat.pixiv.net/roomstepimg.php?id=988003&pos=13418 -> redirects to sketch.pixiv.net/lives
        # http://goods.pixiv.net/c76/images/bg_top5.jpg
        # http://dic.pixiv.net/a/あ～るさん
        elif parsable_url.subdomain in ["sensei", "imgaz", "source", "dev", "chat", "goods", "dic"]:
            raise UnparsableUrl(parsable_url)
        else:
            return None

    @staticmethod
    def _match_no_subdomain(parsable_url: ParsableUrl) -> p.PixivUrl | None:
        instance: p.PixivUrl
        match parsable_url.url_parts:
            # https://www.pixiv.net/en/artworks/46324488
            # https://www.pixiv.net/artworks/46324488
            # http://www.pixiv.net/i/18557054
            # https://www.pixiv.net/en/artworks/83371546#1
            # https://www.pixiv.net/en/artworks/92045058#big_11
            case *_, ("artworks" | "i"), post_id:
                try:
                    instance = p.PixivPostUrl(parsable_url)
                    instance.post_id = int(post_id)
                except ValueError:
                    if "#" in post_id:
                        [post_id, potential_page] = post_id.split("#")
                        if potential_page == "manga":
                            instance = p.PixivPostUrl(parsable_url)
                            instance.post_id = int(post_id)
                        else:
                            potential_page = potential_page.strip("big_")
                            instance = p.PixivImageUrl(parsable_url)
                            [instance.post_id, instance.page] = map(int, [post_id, potential_page])
                            instance.stacc = None
                    else:
                        raise

            # https://www.pixiv.net/u/9202877
            # https://www.pixiv.net/users/9202877
            # https://www.pixiv.net/users/76567/novels
            # https://www.pixiv.net/users/39598149/illustrations?p=1
            # https://www.pixiv.net/user/13569921/series/81967  # TODO: this should be a PixivSeriesUrl
            # https://www.pixiv.net/en/users/9202877
            # https://www.pixiv.net/en/users/76567/novels
            case ([("u" | "users" | "user"), user_id, *_] |
                  ["en", "users", user_id, *_]):
                instance = p.PixivArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            # https://www.pixiv.net/en/artworks/unlisted/ntQchboUi1CsqMhDpo5j"
            case *_, "artworks", "unlisted", unlisted_id:
                instance = p.PixivPostUrl(parsable_url)
                instance.unlisted = True
                instance.post_id = unlisted_id

            # https://www.pixiv.net/stacc/noizave
            case "stacc", stacc:
                instance = p.PixivStaccUrl(parsable_url)
                instance.stacc = stacc

            # http://www.pixiv.net/member_illust.php?mode=medium&illust_id=18557054
            # http://www.pixiv.net/member_illust.php?mode=big&illust_id=18557054
            # http://www.pixiv.net/member_illust.php?mode=manga&illust_id=18557054
            # http://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=18557054&page=1
            # https://www.pixiv.net/index.php?mode=medium\u0026illust_id=612896
            case [("member_illust.php" | "index.php")]:
                instance = p.PixivPostUrl(parsable_url)
                instance.post_id = int(parsable_url.params["illust_id"])

            # https://www.pixiv.net/member.php?id=339253
            # http://www.pixiv.net/novel/member.php?id=76567
            case *_, "member.php":
                instance = p.PixivArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.params["id"])

            # https://www.pixiv.net/requests/7829
            case "requests", request_id:
                instance = p.PixivRequestUrl(parsable_url)
                instance.request_id = int(request_id)

            # https://www.pixiv.net/novel/show.php?id=8465454
            # https://www.pixiv.net/novel/show.php?id=10008846#8
            case "novel", "show.php":
                instance = p.PixivNovelUrl(parsable_url)
                try:
                    instance.novel_id = int(parsable_url.params["id"])
                except ValueError:
                    instance.novel_id = int(parsable_url.params["id"].split("#")[0])

            # https://www.pixiv.net/novel/series/436782
            case *_, "novel", "series", series_id:
                instance = p.PixivNovelSeriesUrl(parsable_url)
                instance.series_id = int(series_id)

            case _:
                # https://www.pixiv.net/contest/neuralcloud
                # http://www.pixiv.net/tags.php?tag=%E5%88%86%E5%89%B2%E9%9C%8A%E5%A4%A2
                # http://www.pixiv.net/group/?id=1992
                if parsable_url.url_parts[0] in ["tags.php", "tags", "contest", "group"]:
                    raise UnparsableUrl(parsable_url)
                if parsable_url.url_parts[0:1] == ["en", "tags"]:
                    raise UnparsableUrl(parsable_url)
                else:
                    return None
        return instance

    @staticmethod
    def _match_sketch_subdomain(parsable_url: ParsableUrl) -> s.PixivSketchUrl | None:
        instance: s.PixivSketchUrl
        match parsable_url.url_parts:
            # https://sketch.pixiv.net/items/5835314698645024323

            case *_, "uploads", "medium", "file", _, _ if parsable_url.subdomain == "img-sketch":  # TODO: figure out these numbers
                instance = s.PixivSketchImageUrl(parsable_url)
            # https://img-sketch.pixiv.net/uploads/medium/file/4463372/8906921629213362989.jpg
            # https://img-sketch.pixiv.net/c/f_540/uploads/medium/file/9986983/8431631593768139653.jpg
            case "items", post_id:
                instance = s.PixivSketchPostUrl(parsable_url)
                instance.post_id = int(post_id)
            # https://sketch.pixiv.net/@user_ejkv8372
            # https://sketch.pixiv.net/@user_ejkv8372/followings
            case stacc, *_ if stacc.startswith("@"):
                instance = s.PixivSketchArtistUrl(parsable_url)
                instance.stacc = stacc
            case _:
                return None

        return instance

    @staticmethod
    def _match_fanbox_path(parsable_url: ParsableUrl) -> f.FanboxUrl | None:
        instance: f.FanboxUrl
        match parsable_url.url_parts:
            # https://pixiv.net/fanbox/creator/1566167/post/39714
            # https://www.pixiv.net/fanbox/creator/1566167/post/39714
            case "fanbox", "creator", pixiv_id, "post", post_id:
                instance = f.FanboxOldPostUrl(parsable_url)
                instance.pixiv_id = int(pixiv_id)
                instance.post_id = int(post_id)

            # https://pixiv.net/fanbox/creator/1566167
            # https://www.pixiv.net/fanbox/creator/1566167
            # https://www.pixiv.net/fanbox/user/3410642
            # https://www.pixiv.net/fanbox/creator/18915237/post
            case "fanbox", ("creator" | "user"), pixiv_id, *_:
                instance = f.FanboxOldArtistUrl(parsable_url)
                instance.pixiv_id = int(pixiv_id)

            # https://www.pixiv.net/fanbox/entry.php?entry_id=1264
            case "fanbox", "entry.php":
                instance = f.FanboxOldPostUrl(parsable_url)
                instance.pixiv_id = None
                instance.post_id = int(parsable_url.params["entry_id"])

            # http://pixiv.net/fanbox/member.php?user_id=3410642
            case "fanbox", "member.php":
                instance = f.FanboxOldArtistUrl(parsable_url)
                instance.pixiv_id = int(parsable_url.params["user_id"])

            # http://www.pixiv.net/fanbox/resources/entry/325/images/5rd4eo6gs2884gs80csgwc0ws8s44c0o.png
            # https://www.pixiv.net/fanbox/resources/entry/50/images/w_1200/2thpjiboyaskg8owg4owcsg48cg4s484.jpeg
            case "fanbox", "resources", "entry", _, "images", *_:
                raise UnparsableUrl(parsable_url)

            case _:
                return None
        return instance

    @staticmethod
    def _match_fanbox_subdomain(parsable_url: ParsableUrl) -> f.FanboxImageUrl | None:
        match parsable_url.url_parts:
            # https://fanbox.pixiv.net/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png  # old
            # https://fanbox.pixiv.net/files/post/207010/y1qrUK90dn63JXqUE21itupM.png
            case ("images" | "files"), "post", post_id, filename:
                instance = f.FanboxImageUrl(parsable_url)
                instance.post_id = int(post_id)
                instance.filename = filename
                instance.pixiv_id = None
                instance.image_type = "post"
            case _:
                return None

        return instance

    @staticmethod
    def _match_comic_subdomain(parsable_url: ParsableUrl) -> c.PixivComicUrl | None:
        instance: c.PixivComicUrl
        match parsable_url.url_parts:
            # https://comic.pixiv.net/works/8683
            case "works", work_id:
                instance = c.PixivComicWorkUrl(parsable_url)
                instance.work_id = int(work_id)
            # https://comic.pixiv.net/viewer/stories/107927
            case *_, "stories", story_id:
                instance = c.PixivComicStoryUrl(parsable_url)
                instance.story_id = int(story_id)
            case _:
                return None

        return instance

    @staticmethod
    def _match_i_subdomain(parsable_url: ParsableUrl) -> p.PixivUrl | None:
        instance: p.PixivUrl
        match parsable_url.url_parts:
            # http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_64x64.jpg
            # http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_s.png
            # http://i3.pixiv.net/img-original/img/2016/05/30/11/53/26/57141110_p0.jpg
            case *_, "img", year, month, day, hour, minute, second, filename:
                instance = p.PixivImageUrl(parsable_url)
                instance.parse_filename(filename, year, month, day, hour, minute, second)
                instance.stacc = None

            # http://i1.pixiv.net/img07/img/pasirism/18557054_p1.png
            # http://i2.pixiv.net/img18/img/evazion/14901720.png
            # http://img18.pixiv.net/img/evazion/14901720.png
            # http://img04.pixiv.net/img/aenobas/20513642_big_p48.jpg
            case *_, "img", stacc, filename:
                instance = p.PixivImageUrl(parsable_url)
                instance.stacc = stacc
                instance.parse_filename(filename)

            # http://i2.pixiv.net/img50/img/ha_ru_17/mobile/38262519_480mw.jpg
            case *_, "img", stacc, "mobile", filename:
                instance = p.PixivImageUrl(parsable_url)
                instance.parse_filename(filename)
                instance.stacc = stacc

            # https://i.pximg.net/img96/img/masao_913555/novel/4472318.jpg
            case *_, "img", stacc, "novel", filename:
                instance = p.PixivNovelImageUrl(parsable_url)
                instance.stacc = stacc
                instance.novel_id = int(filename.split(".")[0])

            # https://img17.pixiv.net/yellow_rabbit/3825834.jpg
            case stacc, filename if (parsable_url.subdomain and parsable_url.subdomain.startswith("img")):
                instance = p.PixivImageUrl(parsable_url)
                instance.stacc = stacc
                instance.parse_filename(filename)

            # http://i2.pixiv.net/img14/profile/muta0083/4810758.jpg
            case *_, "profile", stacc, _:
                instance = p.PixivProfileImageUrl(parsable_url)
                instance.stacc = stacc

            case _:
                return None

        return instance

    test_cases = {
        s.PixivSketchImageUrl: [
            "https://img-sketch.pixiv.net/uploads/medium/file/4463372/8906921629213362989.jpg",
            "https://img-sketch.pixiv.net/c/f_540/uploads/medium/file/9986983/8431631593768139653.jpg",
        ],
        s.PixivSketchPostUrl: [
            "https://sketch.pixiv.net/items/5835314698645024323",
        ],
        s.PixivSketchArtistUrl: [
            "https://sketch.pixiv.net/@user_ejkv8372",
            "https://sketch.pixiv.net/@user_ejkv8372/followings",
        ],
        f.FanboxImageUrl: [
            "https://fanbox.pixiv.net/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png",
            "https://fanbox.pixiv.net/files/post/207010/y1qrUK90dn63JXqUE21itupM.png",
        ],
        f.FanboxOldArtistUrl: [
            "https://pixiv.net/fanbox/creator/1566167",
            "https://www.pixiv.net/fanbox/creator/1566167",
            "https://www.pixiv.net/fanbox/user/3410642",
            "https://www.pixiv.net/fanbox/creator/18915237/post",
            "http://pixiv.net/fanbox/member.php?user_id=3410642",
            "http://www.pixiv.net/fanbox/member.php?user_id=3410642",
        ],
        f.FanboxOldPostUrl: [
            "https://pixiv.net/fanbox/creator/1566167/post/39714",
            "https://www.pixiv.net/fanbox/creator/1566167/post/39714",
            "https://www.pixiv.net/fanbox/entry.php?entry_id=1264"
        ],
        p.PixivArtistUrl: [
            "https://www.pixiv.net/u/9202877",
            "https://www.pixiv.net/users/9202877",
            "https://www.pixiv.net/users/76567/novels",
            "https://www.pixiv.net/users/39598149/illustrations?p=1",
            "https://www.pixiv.net/user/13569921/series/81967",
            "https://www.pixiv.net/en/users/9202877",
            "https://www.pixiv.net/en/users/76567/novels",

            "https://www.pixiv.net/member.php?id=339253",
            "http://www.pixiv.net/novel/member.php?id=76567",
        ],
        p.PixivImageUrl: [
            "http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_64x64.jpg",
            "http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_s.png",

            "http://i3.pixiv.net/img-original/img/2016/05/30/11/53/26/57141110_p0.jpg",

            "https://www.pixiv.net/en/artworks/83371546#1",
            "https://www.pixiv.net/en/artworks/92045058#big_11",

            "http://i1.pixiv.net/img07/img/pasirism/18557054_p1.png",
            "http://i2.pixiv.net/img18/img/evazion/14901720.png",

            "https://img17.pixiv.net/yellow_rabbit/3825834.jpg",
            "http://img18.pixiv.net/img/evazion/14901720.png",
            "http://img04.pixiv.net/img/aenobas/20513642_big_p48.jpg",
        ],
        p.PixivPostUrl: [
            "https://www.pixiv.net/en/artworks/46324488",
            "https://www.pixiv.net/artworks/46324488",
            "http://www.pixiv.net/i/18557054",

            "http://www.pixiv.net/member_illust.php?mode=medium&illust_id=18557054",
            "http://www.pixiv.net/member_illust.php?mode=big&illust_id=18557054",
            "http://www.pixiv.net/member_illust.php?mode=manga&illust_id=18557054",
            "http://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=18557054&page=1",
            "https://www.pixiv.net/index.php?mode=medium\u0026illust_id=612896",

            "https://www.pixiv.net/en/artworks/unlisted/ntQchboUi1CsqMhDpo5j"
        ],
        p.PixivStaccUrl: [
            "https://www.pixiv.net/stacc/noizave",
            "https://blog.pixiv.net/zerousagi/",
        ],
        c.PixivComicStoryUrl: [
            "https://comic.pixiv.net/viewer/stories/107927",
        ],
        c.PixivComicWorkUrl: [
            "https://comic.pixiv.net/works/8683",
        ],
        p.PixivProfileImageUrl: [
            "http://i2.pixiv.net/img14/profile/muta0083/4810758.jpg",
        ],
        p.PixivRequestUrl: [
            "https://www.pixiv.net/requests/7829",
        ],
        p.PixivNovelUrl: [
            "https://www.pixiv.net/novel/show.php?id=8465454",
            "https://www.pixiv.net/novel/show.php?id=10008846#8",
        ],
        p.PixivNovelSeriesUrl: [
            "https://www.pixiv.net/novel/series/436782",
        ],
        p.PixivNovelImageUrl: [
            "http://i4.pixiv.net/img96/img/masao_913555/novel/4472318.jpg",
        ]
    }
