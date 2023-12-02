import re
from datetime import datetime

from pytz import UTC

from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import fanbox as f
from danboorutools.logical.urls import pixiv as p
from danboorutools.logical.urls import pixiv_comic as c
from danboorutools.logical.urls import pixiv_sketch as s
from danboorutools.models.url import UselessUrl

img_subdomain_pattern = re.compile(r"^i(?:mg)?\d*$")


class PixivNetParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> p.PixivUrl | s.PixivSketchUrl | c.PixivComicUrl | f.FanboxUrl | UselessUrl | None:
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
            return p.PixivStaccUrl(parsed_url=parsable_url,
                                   stacc=parsable_url.url_parts[0])
        # https://sensei.pixiv.net/ja/course/30
        # http://imgaz.pixiv.net/img_group/200/1024091/d0928738938a2c8ecba3dd3a57a4c2ad.png
        # https://source.pixiv.net/source/images/contest/050plus-fes.jpg
        # http://dev.pixiv.net/img/event/princessroyale/8.png
        # http://chat.pixiv.net/roomstepimg.php?id=988003&pos=13418 -> redirects to sketch.pixiv.net/lives
        # http://goods.pixiv.net/c76/images/bg_top5.jpg
        # http://dic.pixiv.net/a/あ～るさん
        elif parsable_url.subdomain in ["sensei", "imgaz", "source", "dev", "chat", "goods", "dic"]:
            raise UnparsableUrlError(parsable_url)
        else:
            return None

    @staticmethod
    def _match_no_subdomain(parsable_url: ParsableUrl) -> p.PixivUrl | UselessUrl | None:
        match parsable_url.url_parts:
            # https://www.pixiv.net/en/artworks/46324488
            # https://www.pixiv.net/artworks/46324488
            # http://www.pixiv.net/i/18557054
            # https://www.pixiv.net/en/artworks/83371546#1
            # https://www.pixiv.net/en/artworks/92045058#big_11
            case *_, ("artworks" | "i"), post_id:
                try:
                    return p.PixivPostUrl(parsed_url=parsable_url,
                                          post_id=int(post_id))
                except ValueError:
                    if "#" in post_id:
                        [post_id, potential_page] = post_id.split("#")
                        if potential_page == "manga":
                            return p.PixivPostUrl(parsed_url=parsable_url,
                                                  post_id=int(post_id))
                        else:
                            potential_page = potential_page.strip("big_")
                            return p.PixivImageUrl(parsed_url=parsable_url,
                                                   post_id=int(post_id),
                                                   page=int(potential_page))
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
                return p.PixivArtistUrl(parsed_url=parsable_url,
                                        user_id=int(user_id))

            # https://www.pixiv.net/en/artworks/unlisted/ntQchboUi1CsqMhDpo5j"
            case *_, "artworks", "unlisted", unlisted_id:
                return p.PixivPostUrl(parsed_url=parsable_url,
                                      unlisted=True,
                                      post_id=unlisted_id)

            # https://www.pixiv.net/stacc/noizave
            case "stacc", stacc:
                return p.PixivStaccUrl(parsed_url=parsable_url,
                                       stacc=stacc)

            # http://www.pixiv.net/member_illust.php?mode=medium&illust_id=18557054
            # http://www.pixiv.net/member_illust.php?mode=big&illust_id=18557054
            # http://www.pixiv.net/member_illust.php?mode=manga&illust_id=18557054
            # http://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=18557054&page=1
            # https://www.pixiv.net/index.php?mode=medium\u0026illust_id=612896
            case ("member_illust.php" | "index.php"), :
                return p.PixivPostUrl(parsed_url=parsable_url,
                                      post_id=int(parsable_url.query["illust_id"]))

            # https://www.pixiv.net/member.php?id=339253
            # http://www.pixiv.net/novel/member.php?id=76567
            case *_, "member.php":
                return p.PixivArtistUrl(parsed_url=parsable_url,
                                        user_id=int(parsable_url.query["id"]))

            # https://www.pixiv.net/requests/7829
            case "requests", request_id:
                return p.PixivRequestUrl(parsed_url=parsable_url,
                                         request_id=int(request_id))

            # https://www.pixiv.net/novel/show.php?id=8465454
            # https://www.pixiv.net/novel/show.php?id=10008846#8
            case "novel", "show.php":
                try:
                    novel_id = int(parsable_url.query["id"])
                except ValueError:
                    novel_id = int(parsable_url.query["id"].split("#")[0])

                return p.PixivNovelUrl(parsed_url=parsable_url,
                                       novel_id=novel_id)

            # https://www.pixiv.net/novel/series/436782
            case *_, "novel", "series", series_id:
                return p.PixivNovelSeriesUrl(parsed_url=parsable_url,
                                             series_id=int(series_id))

            case "dashboard", :
                return UselessUrl(parsed_url=parsable_url)

            # http://pixiv.net/manage/illusts/
            case "manage", *_:
                return UselessUrl(parsable_url)

            case id_slug, if id_slug.startswith("#id="):
                return p.PixivArtistUrl(parsed_url=parsable_url,
                                        user_id=int(id_slug.removeprefix("#id=")))

            case _:
                # https://www.pixiv.net/contest/neuralcloud
                # http://www.pixiv.net/tags.php?tag=%E5%88%86%E5%89%B2%E9%9C%8A%E5%A4%A2
                # http://www.pixiv.net/group/?id=1992
                if parsable_url.url_parts[0] in ["tags.php", "tags", "contest", "group"]:
                    raise UnparsableUrlError(parsable_url)
                if parsable_url.url_parts[0:1] == ["en", "tags"]:
                    raise UnparsableUrlError(parsable_url)
                else:
                    return None

    @staticmethod
    def _match_sketch_subdomain(parsable_url: ParsableUrl) -> s.PixivSketchUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://sketch.pixiv.net/items/5835314698645024323
            case *_, "uploads", "medium", "file", _, _ if parsable_url.subdomain == "img-sketch":
                return s.PixivSketchImageUrl(parsed_url=parsable_url)

            # https://img-sketch.pixiv.net/uploads/medium/file/4463372/8906921629213362989.jpg
            # https://img-sketch.pixiv.net/c/f_540/uploads/medium/file/9986983/8431631593768139653.jpg
            case "items", post_id:
                return s.PixivSketchPostUrl(parsed_url=parsable_url,
                                            post_id=int(post_id))

            # https://sketch.pixiv.net/@user_ejkv8372
            # https://sketch.pixiv.net/@user_ejkv8372/followings
            case stacc, *_ if stacc.startswith("@"):
                return s.PixivSketchArtistUrl(parsed_url=parsable_url,
                                              stacc=stacc[1:])

            case _:
                return None

    @staticmethod
    def _match_fanbox_path(parsable_url: ParsableUrl) -> f.FanboxUrl | None:
        match parsable_url.url_parts:
            # https://pixiv.net/fanbox/creator/1566167/post/39714
            # https://www.pixiv.net/fanbox/creator/1566167/post/39714
            case "fanbox", "creator", pixiv_id, "post", post_id:
                return f.FanboxOldPostUrl(parsed_url=parsable_url,
                                          pixiv_id=int(pixiv_id),
                                          post_id=int(post_id))

            # https://pixiv.net/fanbox/creator/1566167
            # https://www.pixiv.net/fanbox/creator/1566167
            # https://www.pixiv.net/fanbox/user/3410642
            # https://www.pixiv.net/fanbox/creator/18915237/post
            case "fanbox", ("creator" | "user"), pixiv_id, *_:
                return f.FanboxOldArtistUrl(parsed_url=parsable_url,
                                            pixiv_id=int(pixiv_id))

            # http://pixiv.net/fanbox/member.php?user_id=3410642
            case "fanbox", "member.php":
                return f.FanboxOldArtistUrl(parsed_url=parsable_url,
                                            pixiv_id=int(parsable_url.query["user_id"]))

            # http://www.pixiv.net/fanbox/resources/entry/325/images/5rd4eo6gs2884gs80csgwc0ws8s44c0o.png
            # https://www.pixiv.net/fanbox/resources/entry/50/images/w_1200/2thpjiboyaskg8owg4owcsg48cg4s484.jpeg
            case "fanbox", "resources", "entry", _, "images", *_:
                raise UnparsableUrlError(parsable_url)

            # https://www.pixiv.net/fanbox/entry.php?entry_id=1264
            case "fanbox", "entry.php":
                raise UnparsableUrlError(parsable_url)  # this is neither the pixiv id nor the post id

            case _:
                return None

    @staticmethod
    def _match_fanbox_subdomain(parsable_url: ParsableUrl) -> f.FanboxAssetUrl | None:
        match parsable_url.url_parts:
            # https://fanbox.pixiv.net/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png  # old
            # https://fanbox.pixiv.net/files/post/207010/y1qrUK90dn63JXqUE21itupM.png
            case ("images" | "files"), "post", post_id, _filename:
                return f.FanboxAssetUrl(parsed_url=parsable_url,
                                        post_id=int(post_id),
                                        pixiv_id=None,
                                        asset_type="post")
            case _:
                return None

    @staticmethod
    def _match_comic_subdomain(parsable_url: ParsableUrl) -> c.PixivComicUrl | None:
        match parsable_url.url_parts:
            # https://comic.pixiv.net/works/8683
            case "works", work_id:
                return c.PixivComicWorkUrl(parsed_url=parsable_url,
                                           post_id=int(work_id))
            # https://comic.pixiv.net/viewer/stories/107927
            case *_, "stories", story_id:
                return c.PixivComicStoryUrl(parsed_url=parsable_url,
                                            story_id=int(story_id))
            case _:
                return None

    @staticmethod
    def _match_i_subdomain(parsable_url: ParsableUrl) -> p.PixivUrl | None:
        match parsable_url.url_parts:
            # http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_64x64.jpg
            # http://i1.pixiv.net/img-inf/img/2011/05/01/23/28/04/18557054_s.png
            # http://i3.pixiv.net/img-original/img/2016/05/30/11/53/26/57141110_p0.jpg
            case *_, "img", year, month, day, hour, minute, second, _filename:
                created_at = datetime(year=int(year), month=int(month), day=int(day),
                                      hour=int(hour), minute=int(minute), second=int(second), tzinfo=UTC)
                stacc = None
            # http://i1.pixiv.net/img07/img/pasirism/18557054_p1.png
            # http://i2.pixiv.net/img18/img/evazion/14901720.png
            # http://img18.pixiv.net/img/evazion/14901720.png
            # http://img04.pixiv.net/img/aenobas/20513642_big_p48.jpg
            case *_, "img", stacc, _filename:
                pass

            # http://i2.pixiv.net/img50/img/ha_ru_17/mobile/38262519_480mw.jpg
            case *_, "img", stacc, "mobile", _filename:
                pass

            # https://i.pximg.net/img96/img/masao_913555/novel/4472318.jpg
            case *_, "img", stacc, "novel", _filename:
                return p.PixivNovelImageUrl(parsed_url=parsable_url,
                                            stacc=stacc,
                                            novel_id=int(parsable_url.stem))

            # https://img17.pixiv.net/yellow_rabbit/3825834.jpg
            case stacc, _filename if (parsable_url.subdomain and parsable_url.subdomain.startswith("img")):
                pass

            # http://i2.pixiv.net/img14/profile/muta0083/4810758.jpg
            case *_, "profile", stacc, _:
                return p.PixivProfileImageUrl(parsed_url=parsable_url,
                                              stacc=stacc)

            case _:
                return None

        post_id, page, unlisted = p.PixivImageUrl.parse_filename(parsable_url.stem)
        instance = p.PixivImageUrl(parsed_url=parsable_url,
                                   stacc=stacc,
                                   post_id=post_id,
                                   page=page,
                                   unlisted=unlisted)
        try:
            instance.created_at = created_at
        except NameError:
            pass
        return instance
