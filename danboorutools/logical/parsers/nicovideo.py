from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors import nicoseiga as ns
from danboorutools.logical.extractors import nicovideo as nv
from danboorutools.logical.extractors import nicovideo_3d as n3
from danboorutools.logical.extractors import nicovideo_commons as nc
from danboorutools.logical.extractors import nicovideo_oekaki as no
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NicovideoJp(UrlParser):
    @classmethod
    def match_url(cls,
                  parsable_url: ParsableUrl
                  ) -> ns.NicoSeigaUrl | no.NicovideoOekakiUrl | n3.Nicovideo3dUrl | nv.NicovideoUrl | nc.NicovideoCommonsUrl | None:
        if parsable_url.subdomain.endswith("seiga"):
            return cls._match_seiga(parsable_url)
        elif parsable_url.subdomain in ["", "www", "q", "nine", "ext", "sp"]:
            return cls._match_nicovideo(parsable_url)
        elif parsable_url.subdomain == "dic":
            return cls._match_oekaki(parsable_url)
        elif parsable_url.subdomain == "3d":
            return cls._match_3d(parsable_url)
        elif parsable_url.subdomain.endswith("commons"):
            return cls._match_commons(parsable_url)
        elif parsable_url.subdomain == "com":
            return cls._match_com(parsable_url)
        elif parsable_url.subdomain == "game":
            return cls._match_game(parsable_url)

        # http://ch.nicovideo.jp/finalcake
        # http://nivent.nicovideo.jp/ni1675
        # http://chokuhan.nicovideo.jp/products/embed/1257
        # http://info.nicovideo.jp/seiga/imas_illust_chokaigi3/
        elif parsable_url.subdomain in ("ch", "nivent", "chokuhan", "info", "bmimg"):
            raise UnparsableUrl(parsable_url)
        else:
            return None

    @staticmethod
    def _match_seiga(parsable_url: ParsableUrl) -> ns.NicoSeigaUrl | None:
        instance: ns.NicoSeigaUrl

        match parsable_url.url_parts:
            # https://seiga.nicovideo.jp/seiga/im520647  # (anonymous artist)
            # https://seiga.nicovideo.jp/seiga/im3521156
            # https://sp.seiga.nicovideo.jp/seiga/im3521156
            # https://sp.seiga.nicovideo.jp/seiga/#!/im6012363
            # http://seiga.nicovideo.jp/seiga/im4087382#_=_
            case "seiga", illust_id if illust_id.startswith("im"):
                instance = ns.NicoSeigaIllustUrl(parsable_url)
                instance.illust_id = int(illust_id[2:].split("#")[0])

            # https://seiga.nicovideo.jp/image/source/3521156
            # https://seiga.nicovideo.jp/image/source/4744553
            case "image", "source", image_id:
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id)
                instance.image_type = None

            # https://seiga.nicovideo.jp/user/illust/456831
            # https://sp.seiga.nicovideo.jp/user/illust/20542122
            # https://ext.seiga.nicovideo.jp/user/illust/20542122
            case "user", "illust", user_id:
                instance = ns.NicoSeigaArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            case "seiga", "#!", illust_id if illust_id.startswith("im"):
                instance = ns.NicoSeigaIllustUrl(parsable_url)
                instance.illust_id = int(illust_id[2:])

            # https://seiga.nicovideo.jp/watch/mg316708
            # https://sp.seiga.nicovideo.jp/watch/mg316708
            case "watch", manga_id if manga_id.startswith("mg"):
                instance = ns.NicoSeigaMangaUrl(parsable_url)
                instance.manga_id = int(manga_id[2:])

            # https://seiga.nicovideo.jp/image/source?id=3521156
            # https://seiga.nicovideo.jp/image/redirect?id=3583893
            case "image", ("redirect" | "source"):
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(parsable_url.query["id"])
                instance.image_type = None

            # http://seiga.nicovideo.jp/manga/list?user_id=23839737
            # http://sp.seiga.nicovideo.jp/manga/list?user_id=23839737
            case "manga", "list":
                instance = ns.NicoSeigaArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.query["user_id"])

            # http://seiga.nicovideo.jp/manga/rchero
            case "manga", comic_id:
                instance = ns.NicoSeigaComicUrl(parsable_url)
                instance.comic_id = comic_id

            # https://seiga.nicovideo.jp/comic/1571
            case "comic", comic_id:
                instance = ns.NicoSeigaComicUrl(parsable_url)
                instance.comic_id = int(comic_id)

            case "clip", _:
                # anonymous album: https://seiga.nicovideo.jp/clip/191765
                raise UnparsableUrl(parsable_url)

            case ("tag" | "search"), _:
                # http://seiga.nicovideo.jp/tag/%E3%83%97%E3%83%AC%E3%83%87%E3%82%BF%E3%83%BC
                # http://seiga.nicovideo.jp/search/halo?target=illust
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance

    @staticmethod
    def _match_nicovideo(parsable_url: ParsableUrl) -> nv.NicovideoUrl | None:
        instance: nv.NicovideoUrl

        match parsable_url.url_parts:
            # https://www.nicovideo.jp/watch/sm36465441
            # https://www.nicovideo.jp/watch/nm36465441
            # http://nine.nicovideo.jp/watch/nm13933079
            # http://www.nicovideo.jp/watch/1488526447
            case "watch", video_id if video_id[0:2] in ("nm", "sm") or video_id.isnumeric():
                instance = nv.NicovideoVideoUrl(parsable_url)
                instance.video_id = video_id

            # http://www.nicovideo.jp/mylist/2858074/4602763
            case "user", user_id, "mylist", _:
                instance = nv.NicovideoArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            # https://www.nicovideo.jp/user/4572975
            # https://www.nicovideo.jp/user/20446930/mylist/28674289
            # https://q.nicovideo.jp/users/18700356
            case ("users" | "user"), user_id:
                instance = nv.NicovideoArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            # http://www.nicovideo.jp/mylist/21474275
            # http://www.nicovideo.jp/mylist/37220827#+sort=1
            case "mylist", list_id:
                instance = nv.NicovideoListUrl(parsable_url)
                try:
                    instance.list_id = int(list_id)
                except ValueError:
                    instance.list_id = int(list_id.split("#")[0])

            case "mylist", user_id, _:
                instance = nv.NicovideoArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            case "my", "mylist", "#", list_id:
                instance = nv.NicovideoListUrl(parsable_url)
                instance.list_id = int(list_id)

            case "thumb_user", user_id:
                instance = nv.NicovideoArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            # http://www.nicovideo.jp/search/東方恥辱日記
            case "search", *_:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance

    @staticmethod
    def _match_oekaki(parsable_url: ParsableUrl) -> no.NicovideoOekakiUrl | None:
        instance: no.NicovideoOekakiUrl

        match parsable_url.url_parts:
            # https://dic.nicovideo.jp/oekaki/176310.png
            case "oekaki", _filename:
                instance = no.NicovideoOekakiImageUrl(parsable_url)
                instance.post_id = int(parsable_url.stem)

            # https://dic.nicovideo.jp/oekaki_id/340604
            case "oekaki_id", post_id:
                instance = no.NicovideoOekakiPostUrl(parsable_url)
                instance.post_id = int(post_id)

            # https://dic.nicovideo.jp/u/11141663
            case "u", user_id:
                instance = no.NicovideoOekakiArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            # https://dic.nicovideo.jp/r/u/10846063/2063955
            case "r", "u", user_id, _:
                instance = no.NicovideoOekakiArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            # http://dic.nicovideo.jp/a/手錠の人
            # http://dic.nicovideo.jp/id/4783847
            # http://dic.nicovideo.jp/l/七姫
            case ("id" | "a" | "l"), _:
                raise UnparsableUrl(parsable_url)

            # https://dic.nicovideo.jp/b/a/%E3%83%A1%E3%83%88/31-#36
            case "b", ("a" | "u"), _, _:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance

    @staticmethod
    def _match_3d(parsable_url: ParsableUrl) -> n3.Nicovideo3dUrl | None:
        instance: n3.Nicovideo3dUrl

        match parsable_url.url_parts:

            # https://3d.nicovideo.jp/works/td28606
            case "works", post_id:
                instance = n3.Nicovideo3dPostUrl(parsable_url)
                instance.post_id = int(post_id.removeprefix("td"))

            # https://3d.nicovideo.jp/users/109584
            # https://3d.nicovideo.jp/users/29626631/works
            case "users", user_id, *_:
                instance = n3.Nicovideo3dArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            # https://3d.nicovideo.jp/u/siobi
            case "u", username:
                instance = n3.Nicovideo3dArtistUrl(parsable_url)
                instance.username = username
                instance.user_id = None

            # http://3d.nicovideo.jp/alicia/img/header_character3d.png
            case _, "img", _:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance

    @staticmethod
    def _match_commons(parsable_url: ParsableUrl) -> nc.NicovideoCommonsUrl | None:
        instance: nc.NicovideoCommonsUrl

        match parsable_url.url_parts:
            # https://commons.nicovideo.jp/material/nc138051
            case "material", commons_id:
                instance = nc.NicovideoCommonsPostUrl(parsable_url)
                instance.commons_id = commons_id

            # https://commons.nicovideo.jp/user/696839
            case "user", user_id:
                instance = nc.NicovideoCommonsArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            # https://deliver.commons.nicovideo.jp/thumbnail/nc285306?size=ll
            case "thumbnail", commons_id:
                instance = nc.NicovideoCommonsPostUrl(parsable_url)
                instance.commons_id = commons_id

            case _:
                return None

        return instance

    @staticmethod
    def _match_com(parsable_url: ParsableUrl) -> nv.NicovideoCommunityUrl | None:

        match parsable_url.url_parts:
            # https://com.nicovideo.jp/community/co24880
            case "community", community_id:
                instance = nv.NicovideoCommunityUrl(parsable_url)
                instance.community_id = int(community_id.removeprefix("co"))

            case _:
                return None

        return instance

    @staticmethod
    def _match_game(parsable_url: ParsableUrl) -> nv.NicovideoGameArtistUrl | None:

        match parsable_url.url_parts:
            # https://game.nicovideo.jp/atsumaru/users/7757217
            case "atsumaru", "users", user_id:
                instance = nv.NicovideoGameArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            case _:
                return None

        return instance


class NimgJpParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ns.NicoSeigaImageUrl | None:
        match parsable_url.url_parts:
            # https://dcdn.cdn.nimg.jp/priv/62a56a7f67d3d3746ae5712db9cac7d465f4a339/1592186183/10466669
            case "priv", _, _, image_id:
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id)
                instance.image_type = None

            # https://dcdn.cdn.nimg.jp/nicoseiga/lohas/o/8ba0a9b2ea34e1ef3b5cc50785bd10cd63ec7e4a/1592187477/10466669
            case "nicoseiga", "lohas", "o", _, _, image_id:
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id[:-1])
                instance.image_type = None

            # https://dcdn.cdn.nimg.jp/niconews/articles/body_images/5544288/5b4672e6da49c2dd195a95caca424c20ff8f67f9b23cc6689fc28719de4c6037b3839d2d8757ceb8e25cfd6ce98093d71101831bbfc39e26baaca915ce32633d
            case "niconews", *_:
                raise UnparsableUrl(parsable_url)

            # https://img.cdn.nimg.jp/s/nicovideo/thumbnails/39681749/39681749.7860892.original/r1280x720l?key=8bc8ebb87e7286cef4e3303bb32e15b93e99c959e9fe4ce2af66884a4167024a  # -> https://www.nicovideo.jp/watch/sm39681749
            case _, "nicovideo", *_:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance


class NicoseigaJpParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ns.NicoSeigaImageUrl | None:
        match parsable_url.url_parts:
            # https://lohas.nicoseiga.jp/o/971eb8af9bbcde5c2e51d5ef3a2f62d6d9ff5552/1589933964/3583893  # https://seiga.nicovideo.jp/seiga/im3583893
            case "o", _, _, illust_id:
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(illust_id)
                instance.image_type = "illust"

            # https://lohas.nicoseiga.jp/priv/b80f86c0d8591b217e7513a9e175e94e00f3c7a1/1384936074/3583893  # https://seiga.nicovideo.jp/seiga/im3583893
            # https://lohas.nicoseiga.jp/priv/3521156?e=1382558156&h=f2e089256abd1d453a455ec8f317a6c703e2cedf  # https://seiga.nicovideo.jp/seiga/im3521156
            case "priv", *_, image_id:
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id)
                instance.image_type = None

            # https://lohas.nicoseiga.jp/thumb/2163478i  # https://seiga.nicovideo.jp/seiga/im2163478
            # https://lohas.nicoseiga.jp/thumb/1591081q  # https://seiga.nicovideo.jp/seiga/im1591081
            case "thumb", illust_id if illust_id.endswith("i") or illust_id.endswith("q"):
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(illust_id[:-1])
                instance.image_type = "illust"

            # https://lohas.nicoseiga.jp/thumb/4744553p  # https://seiga.nicovideo.jp/watch/mg122274
            case "thumb", image_id if image_id.endswith("p"):
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id[:-1])
                instance.image_type = None

            # https://lohas.nicoseiga.jp/material/5746c5/4459092?
            case "material", *_:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance


class NicomangaJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> ns.NicoSeigaImageUrl | None:
        match parsable_url.url_parts:
            # https://deliver.cdn.nicomanga.jp/thumb/7891081p?1590171867
            case "thumb", image_id if image_id.endswith("p"):
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id[:-1])
                instance.image_type = None

            # https://drm.cdn.nicomanga.jp/image/d4a2faa68ec34f95497db6601a4323fde2ccd451_9537/8017978p?1570012695
            case "image", _, image_id if image_id.endswith("p"):
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id[:-1])
                instance.image_type = None

            case _:
                return None

        return instance


class NicoMs(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> nv.NicovideoUrl | ns.NicoSeigaUrl | None:
        instance: nv.NicovideoUrl | ns.NicoSeigaUrl

        if len(parsable_url.url_parts) == 1:
            match (_id := parsable_url.url_parts[0])[:2]:

                # https://nico.ms/im10922621
                case "im":
                    instance = ns.NicoSeigaIllustUrl(parsable_url)
                    instance.illust_id = int(_id[2:])

                # https://nico.ms/mg310193
                case "mg":
                    instance = ns.NicoSeigaMangaUrl(parsable_url)
                    instance.manga_id = int(_id[2:])

                # https://nico.ms/nm36465441
                # https://nico.ms/sm36465441
                case ("sm" | "nm"):
                    instance = nv.NicovideoVideoUrl(parsable_url)
                    instance.video_id = _id

                # "http://nico.ms/co2744246
                case "co":
                    instance = nv.NicovideoCommunityUrl(parsable_url)
                    instance.community_id = int(_id[2:])

                case _:
                    return None
        else:
            match parsable_url.url_parts:

                # http://nico.ms/user/43606505
                case "user", user_id:
                    instance = nv.NicovideoArtistUrl(parsable_url)
                    instance.user_id = int(user_id)

                case _:
                    return None

        return instance
