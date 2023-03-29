from datetime import datetime

import pytz
from pytz import UTC

from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls.booth import BoothImageUrl, BoothProfileImageUrl, BoothUrl
from danboorutools.logical.urls.fanbox import FanboxArtistImageUrl, FanboxImageUrl, FanboxUrl
from danboorutools.logical.urls.pixiv import PixivGalleryAssetUrl, PixivImageUrl, PixivNovelImageUrl, PixivProfileImageUrl, PixivUrl
from danboorutools.logical.urls.pixiv_sketch import PixivSketchImageUrl


class PixivPaths:
    main_image_paths = ("img-original", "img-master", "custom-thumb", "img-zip-ugoira", "img-inf")
    novel_image_paths = ("novel-cover-original", "novel-cover-master")


class PximgNetParser(UrlParser):
    test_cases = {
        FanboxImageUrl: [
            "https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg",
            "https://pixiv.pximg.net/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg",
        ],
        FanboxArtistImageUrl: [
            "https://pixiv.pximg.net/c/400x400_90_a2_g5/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg",
            "https://pixiv.pximg.net/c/1620x580_90_a2_g5/fanbox/public/images/creator/1566167/cover/QqxYtuWdy4XWQx1ZLIqr4wvA.jpeg",
            "https://pixiv.pximg.net/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg",
        ],
        PixivImageUrl: [
            "https://i-f.pximg.net/img-original/img/2020/02/19/00/40/18/79584713_p0.png",
            "https://i.pximg.net/c/250x250_80_a2/img-master/img/2014/10/29/09/27/19/46785915_p0_square1200.jpg",
            "https://i.pximg.net/c/360x360_70/custom-thumb/img/2022/03/08/00/00/56/96755248_p0_custom1200.jpg",
            "https://i.pximg.net/img-master/img/2014/10/03/18/10/20/46324488_p0_master1200.jpg",
            "https://i.pximg.net/img-original/img/2014/10/03/18/10/20/46324488_p0.png",
            "https://i.pximg.net/img-original/img/2019/05/27/17/59/33/74932152_ugoira0.jpg",
            "https://i.pximg.net/img-zip-ugoira/img/2016/04/09/14/25/29/56268141_ugoira1920x1080.zip",

            "https://i.pximg.net/img-inf/img/2014/09/11/00/16/59/45906923_s.jpg",

            "https://i.pximg.net/img25/img/nwqkqr/22218203.jpg",

            "https://i.pximg.net/img-original/img/2018/03/30/10/50/16/67982747-04d810bf32ebd071927362baec4057b6_p0.png",
        ],
        PixivProfileImageUrl: [
            "https://i.pximg.net/user-profile/img/2021/08/25/00/00/40/21290212_0374c372d602a6ec6b311764b0168a13_170.jpg",
        ],
        PixivSketchImageUrl: [
            "https://img-sketch.pximg.net/c!/w=540,f=webp:jpeg/uploads/medium/file/4463372/8906921629213362989.jpg",
        ],
        BoothImageUrl: [
            "https://booth.pximg.net/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d_base_resized.jpg",
            "https://booth.pximg.net/c/300x300_a2_g5/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d_base_resized.jpg",
            "https://booth.pximg.net/c/72x72_a2_g5/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d_base_resized.jpg",
            "https://booth.pximg.net/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d.jpeg",
            "https://booth.pximg.net/b242a7bd-0747-48c4-891d-9e8552edd5d7/i/3746752/52dbee27-7ad2-4048-9c1d-827eee36625c.jpg",
        ],
        BoothProfileImageUrl: [
            "https://booth.pximg.net/c/128x128/users/3193929/icon_image/5be9eff4-1d9e-4a79-b097-33c1cd4ad314_base_resized.jpg",
            "https://booth.pximg.net/users/3193929/icon_image/5be9eff4-1d9e-4a79-b097-33c1cd4ad314.png",
        ],
        PixivNovelImageUrl: [
            "https://i.pximg.net/c/600x600/novel-cover-master/img/2018/08/18/19/45/23/10008846_215387d3665210eed0a7cc564e4c93f3_master1200.jpg",
            "https://i.pximg.net/novel-cover-original/img/2022/11/17/15/07/44/tei336490527346_a4ef4696530c4675fabef4b8e6e186c9.jpg",
            "https://i.pximg.net/img96/img/masao_913555/novel/4472318.jpg",
        ],
        PixivGalleryAssetUrl: [
            "https://i.pximg.net/background/img/2021/11/19/01/48/36/3767624_473f1bc024142eef43c80d2b0061b25a.jpg",
            "https://i.pximg.net/workspace/img/2016/06/23/13/21/30/3968542_1603f967a310f7b03629b07a8f811c13.jpg",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> (PixivUrl | FanboxUrl | PixivSketchImageUrl | BoothUrl | None):
        if parsable_url.subdomain == "i" or parsable_url.subdomain.startswith("i-"):
            return cls._match_i_piximg(parsable_url)
        elif parsable_url.subdomain == "booth":
            return cls._match_booth(parsable_url)
        else:
            return cls._match_everything_else(parsable_url)

    @staticmethod
    def _match_i_piximg(parsable_url: ParsableUrl) -> PixivUrl | None:
        match parsable_url.url_parts:
            # https://i-f.pximg.net/img-original/img/2020/02/19/00/40/18/79584713_p0.png
            # https://i.pximg.net/c/250x250_80_a2/img-master/img/2014/10/29/09/27/19/46785915_p0_square1200.jpg
            # https://i.pximg.net/c/360x360_70/custom-thumb/img/2022/03/08/00/00/56/96755248_p0_custom1200.jpg
            # https://i.pximg.net/img-master/img/2014/10/03/18/10/20/46324488_p0_master1200.jpg
            # https://i.pximg.net/img-original/img/2014/10/03/18/10/20/46324488_p0.png
            # https://i.pximg.net/img-original/img/2019/05/27/17/59/33/74932152_ugoira0.jpg
            # https://i.pximg.net/img-zip-ugoira/img/2016/04/09/14/25/29/56268141_ugoira1920x1080.zip

            # https://i.pximg.net/img-original/img/2018/03/30/10/50/16/67982747-04d810bf32ebd071927362baec4057b6_p0.png

            case *_, image_dir, "img", year, month, day, hour, minute, second, _filename if image_dir in PixivPaths.main_image_paths:
                stacc = None

                created_at = datetime(year=int(year), month=int(month), day=int(day),
                                      hour=int(hour), minute=int(minute), second=int(second), tzinfo=UTC)

            # https://i.pximg.net/user-profile/img/2021/08/25/00/00/40/21290212_0374c372d602a6ec6b311764b0168a13_170.jpg
            case *_, "user-profile", "img", year, month, day, hour, minute, second, filename:
                instance = PixivProfileImageUrl(parsed_url=parsable_url,
                                                stacc=None)
                created_at = datetime(year=int(year), month=int(month), day=int(day),
                                      hour=int(hour), minute=int(minute), second=int(second), tzinfo=pytz.UTC)
                return instance

            # https://i.pximg.net/novel-cover-original/img/2022/11/17/15/07/44/tei336490527346_a4ef4696530c4675fabef4b8e6e186c9.jpg
            # https://i.pximg.net/c/600x600/novel-cover-master/img/2018/08/18/19/45/23/10008846_215387d3665210eed0a7cc564e4c93f3_master1200.jpg
            case *_, image_dir, "img", year, month, day, hour, minute, second, filename if image_dir in PixivPaths.novel_image_paths:
                created_at = datetime(year=int(year), month=int(month), day=int(day),
                                      hour=int(hour), minute=int(minute), second=int(second), tzinfo=pytz.UTC)
                try:
                    novel_id = int(filename.split("_")[0])
                except ValueError:
                    novel_id = None
                return PixivNovelImageUrl(parsed_url=parsable_url,
                                          novel_id=novel_id)

            # https://i.pximg.net/background/img/2021/11/19/01/48/36/3767624_473f1bc024142eef43c80d2b0061b25a.jpg
            # https://i.pximg.net/workspace/img/2016/06/23/13/21/30/3968542_1603f967a310f7b03629b07a8f811c13.jpg
            case *_, ("background" | "workspace"), "img", year, month, day, hour, minute, second, _filename:
                return PixivGalleryAssetUrl(parsed_url=parsable_url,
                                            user_id=int(parsable_url.stem.split("_")[0]))
                # instance.created_at = datetime(year=int(year), month=int(month), day=int(day),
                #                                hour=int(hour), minute=int(minute), second=int(second), tzinfo=pytz.UTC)

            # https://i.pximg.net/img25/img/nwqkqr/22218203.jpg
            case *_, "img", stacc, filename:
                pass

            # https://i.pximg.net/img96/img/masao_913555/novel/4472318.jpg
            case *_, "img", stacc, "novel", filename:
                return PixivNovelImageUrl(parsed_url=parsable_url,
                                          novel_id=int(parsable_url.stem),
                                          stacc=stacc)
            case _:
                return None

        post_id, page, unlisted = PixivImageUrl.parse_filename(parsable_url.stem)
        instance = PixivImageUrl(parsed_url=parsable_url,  # type: ignore[assignment]
                                 stacc=stacc,
                                 post_id=post_id,
                                 page=page,
                                 unlisted=unlisted)
        try:
            instance.created_at = created_at
        except NameError:
            pass
        return instance

    @staticmethod
    def _match_booth(parsable_url: ParsableUrl) -> BoothUrl | None:
        match parsable_url.url_parts:
            # https://booth.pximg.net/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d_base_resized.jpg
            # https://booth.pximg.net/c/300x300_a2_g5/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d_base_resized.jpg
            # https://booth.pximg.net/c/72x72_a2_g5/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d_base_resized.jpg
            # https://booth.pximg.net/8bb9e4e3-d171-4027-88df-84480480f79d/i/2864768/00cdfef0-e8d5-454b-8554-4885a7e4827d.jpeg
            # https://booth.pximg.net/b242a7bd-0747-48c4-891d-9e8552edd5d7/i/3746752/52dbee27-7ad2-4048-9c1d-827eee36625c.jpg

            case *_, "i", post_id, _:
                return BoothImageUrl(parsed_url=parsable_url,
                                     item_id=int(post_id))

            # https://booth.pximg.net/c/128x128/users/3193929/icon_image/5be9eff4-1d9e-4a79-b097-33c1cd4ad314_base_resized.jpg
            # https://booth.pximg.net/users/3193929/icon_image/5be9eff4-1d9e-4a79-b097-33c1cd4ad314.png
            case *_, "users", user_id, "icon_image", _:
                return BoothProfileImageUrl(parsed_url=parsable_url,
                                            user_id=int(user_id))

            case _:
                return None

    @staticmethod
    def _match_everything_else(parsable_url: ParsableUrl) -> PixivSketchImageUrl | FanboxUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://img-sketch.pximg.net/c!/w=540,f=webp:jpeg/uploads/medium/file/4463372/8906921629213362989.jpg
            case *_, "uploads", "medium", "file", _, _ if parsable_url.subdomain == "img-sketch":  # TODO: figure out these numbers
                return PixivSketchImageUrl(parsed_url=parsable_url)

            # https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg
            # https://pixiv.pximg.net/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg
            case *_, "fanbox", "public", "images", "post", post_id, "cover" as image_type, _filename:
                return FanboxImageUrl(parsed_url=parsable_url,
                                      post_id=int(post_id),
                                      pixiv_id=None,
                                      image_type=image_type)

            # https://pixiv.pximg.net/c/400x400_90_a2_g5/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg
            # https://pixiv.pximg.net/c/1620x580_90_a2_g5/fanbox/public/images/creator/1566167/cover/QqxYtuWdy4XWQx1ZLIqr4wvA.jpeg
            # https://pixiv.pximg.net/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg",  # dead
            case *_, "fanbox", "public", "images", "creator", pixiv_id, ("profile" | "cover") as image_type, _filename:
                return FanboxArtistImageUrl(parsed_url=parsable_url,
                                            pixiv_id=int(pixiv_id),
                                            image_type=image_type)

            case _:
                return None
