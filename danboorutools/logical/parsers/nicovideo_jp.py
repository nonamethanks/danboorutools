from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors import nicoseiga as ns
from danboorutools.logical.extractors import nicovideo as nv
from danboorutools.logical.extractors import nicovideo_3d as n3
from danboorutools.logical.extractors import nicovideo_commons as nc
from danboorutools.logical.extractors import nicovideo_oekaki as no
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NicovideoJp(UrlParser):
    test_cases = {
        ns.NicoSeigaIllustUrl: [
            "https://seiga.nicovideo.jp/seiga/im520647",  # (anonymous artist)
            "https://seiga.nicovideo.jp/seiga/im3521156",
            "https://sp.seiga.nicovideo.jp/seiga/im3521156",
            "https://sp.seiga.nicovideo.jp/seiga/#!/im6012363",
            "http://seiga.nicovideo.jp/seiga/im4087382#_=_",
        ],
        ns.NicoSeigaMangaUrl: [
            "https://seiga.nicovideo.jp/watch/mg316708",
            "https://sp.seiga.nicovideo.jp/watch/mg316708",
        ],
        ns.NicoSeigaArtistUrl: [
            "https://seiga.nicovideo.jp/user/illust/456831",
            "https://sp.seiga.nicovideo.jp/user/illust/20542122",
            "https://ext.seiga.nicovideo.jp/user/illust/20542122",
            "http://seiga.nicovideo.jp/manga/list?user_id=23839737",
            "http://sp.seiga.nicovideo.jp/manga/list?user_id=23839737",
            "http://seiga.nicovideo.jp/manga/list?user_id=23839737",
            "http://sp.seiga.nicovideo.jp/manga/list?user_id=23839737",
        ],
        ns.NicoSeigaImageUrl: [
            "https://seiga.nicovideo.jp/image/source/3521156",
            "https://seiga.nicovideo.jp/image/source/4744553",
            "https://seiga.nicovideo.jp/image/source?id=3521156",
            "https://seiga.nicovideo.jp/image/redirect?id=3583893",
        ],
        nv.NicovideoVideoUrl: [
            "https://www.nicovideo.jp/watch/sm36465441",
            "https://www.nicovideo.jp/watch/nm36465441",
            "http://nine.nicovideo.jp/watch/nm13933079",
            "http://www.nicovideo.jp/watch/1488526447",
        ],
        nv.NicovideoArtistUrl: [
            "https://www.nicovideo.jp/user/4572975",
            "https://www.nicovideo.jp/user/20446930/mylist/28674289",
            "https://q.nicovideo.jp/users/18700356",
            "http://www.nicovideo.jp/mylist/2858074/4602763",
        ],
        no.NicovideoOekakiImageUrl: [
            "https://dic.nicovideo.jp/oekaki/176310.png",
        ],
        no.NicovideoOekakiPostUrl: [
            "https://dic.nicovideo.jp/oekaki_id/340604",
        ],
        no.NicovideoOekakiArtistUrl: [
            "https://dic.nicovideo.jp/u/11141663",
            "https://dic.nicovideo.jp/r/u/10846063/2063955"
        ],
        n3.Nicovideo3dArtistUrl: [
            "https://3d.nicovideo.jp/users/109584",
            "https://3d.nicovideo.jp/users/29626631/works",
            "https://3d.nicovideo.jp/u/siobi",
        ],
        n3.Nicovideo3dPostUrl: [
            "https://3d.nicovideo.jp/works/td28606",
        ],
        nv.NicovideoCommunityUrl: [
            "https://com.nicovideo.jp/community/co24880",
        ],
        nv.NicovideoListUrl: [
            "http://www.nicovideo.jp/mylist/21474275",
            "http://www.nicovideo.jp/mylist/37220827#+sort=1",
        ],
        ns.NicoSeigaComicUrl: [
            "https://seiga.nicovideo.jp/comic/1571",
            "http://seiga.nicovideo.jp/manga/rchero",
        ],
        nv.NicovideoGameArtistUrl: [
            "https://game.nicovideo.jp/atsumaru/users/7757217"
        ],
        nc.NicovideoCommonsArtistUrl: [
            "https://commons.nicovideo.jp/user/696839",
        ],
        nc.NicovideoCommonsPostUrl: [
            "https://commons.nicovideo.jp/material/nc138051",
            "https://deliver.commons.nicovideo.jp/thumbnail/nc285306?size=ll",
        ]
    }

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
            case "seiga", illust_id if illust_id.startswith("im"):
                instance = ns.NicoSeigaIllustUrl(parsable_url)
                instance.illust_id = int(illust_id[2:].split("#")[0])

            case "image", "source", image_id:
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(image_id)
                instance.image_type = None

            case "user", "illust", user_id:
                instance = ns.NicoSeigaArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            case "seiga", "#!", illust_id if illust_id.startswith("im"):
                instance = ns.NicoSeigaIllustUrl(parsable_url)
                instance.illust_id = int(illust_id[2:])

            case "watch", manga_id if manga_id.startswith("mg"):
                instance = ns.NicoSeigaMangaUrl(parsable_url)
                instance.manga_id = int(manga_id[2:])

            case "image", ("redirect" | "source"):
                instance = ns.NicoSeigaImageUrl(parsable_url)
                instance.image_id = int(parsable_url.query["id"])
                instance.image_type = None

            case "manga", "list":
                instance = ns.NicoSeigaArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.query["user_id"])

            case "manga", comic_id:
                instance = ns.NicoSeigaComicUrl(parsable_url)
                instance.comic_id = comic_id

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
            case "watch", video_id if video_id[0:2] in ("nm", "sm") or video_id.isnumeric():
                instance = nv.NicovideoVideoUrl(parsable_url)
                instance.video_id = video_id

            case "user", user_id, "mylist", _:
                instance = nv.NicovideoArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            case ("users" | "user"), user_id:
                instance = nv.NicovideoArtistUrl(parsable_url)
                instance.user_id = int(user_id)

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
            case "oekaki", _filename:
                instance = no.NicovideoOekakiImageUrl(parsable_url)
                instance.post_id = int(parsable_url.stem)

            case "oekaki_id", post_id:
                instance = no.NicovideoOekakiPostUrl(parsable_url)
                instance.post_id = int(post_id)

            case "u", user_id:
                instance = no.NicovideoOekakiArtistUrl(parsable_url)
                instance.user_id = int(user_id)

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
            case "works", post_id:
                instance = n3.Nicovideo3dPostUrl(parsable_url)
                instance.post_id = int(post_id.removeprefix("td"))

            case "users", user_id, *_:
                instance = n3.Nicovideo3dArtistUrl(parsable_url)
                instance.user_id = int(user_id)

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
            case "material", commons_id:
                instance = nc.NicovideoCommonsPostUrl(parsable_url)
                instance.commons_id = commons_id

            case "user", user_id:
                instance = nc.NicovideoCommonsArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            case "thumbnail", commons_id:
                instance = nc.NicovideoCommonsPostUrl(parsable_url)
                instance.commons_id = commons_id

            case _:
                return None

        return instance

    @staticmethod
    def _match_com(parsable_url: ParsableUrl) -> nv.NicovideoCommunityUrl | None:

        match parsable_url.url_parts:
            case "community", community_id:
                instance = nv.NicovideoCommunityUrl(parsable_url)
                instance.community_id = int(community_id.removeprefix("co"))

            case _:
                return None

        return instance

    @staticmethod
    def _match_game(parsable_url: ParsableUrl) -> nv.NicovideoGameArtistUrl | None:

        match parsable_url.url_parts:
            case "atsumaru", "users", user_id:
                instance = nv.NicovideoGameArtistUrl(parsable_url)
                instance.user_id = int(user_id)

            case _:
                return None

        return instance
