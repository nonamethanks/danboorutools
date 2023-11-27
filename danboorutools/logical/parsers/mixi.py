import re

from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import mixi as m
from danboorutools.models.url import UnsupportedUrl, UselessUrl


class MixiJpParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> m.MixiUrl | UselessUrl | UnsupportedUrl | None:
        match parsable_url.url_parts:
            # http://mixi.jp/show_profile.pl?id=31861634
            # http://mixi.jp/show_friend.pl?id=1225482
            # http://mixi.jp/show_friend.pl?id=610331/
            # http://mixi.jp/list_album.pl?id=541227
            # https://mixi.jp/list_diary.pl?id=396054
            # http://m.mixi.jp/photo_view_album.pl?guid=ON&owner_id=25119233&album_id=8322560
            case ("show_profile.pl" | "show_friend.pl" | "list_album.pl" | "list_diary.pl" | "list_voice.pl"), :
                keys = "id", "pt", "owner_id"
                for key in keys:
                    if profile_id := parsable_url.query.get(key, "").strip("/"):
                        return m.MixiProfileUrl(parsed_url=parsable_url, profile_id=int(profile_id))
                return None

            # https://photo.mixi.jp/view_album.pl?album_id=8322560&owner_id=25119233
            # http://m.mixi.jp/photo_view_album.pl?guid=ON&owner_id=25119233&album_id=8322560
            case ("photo_view_album.pl" | "view_album.pl"), :
                album_id = parsable_url.query.get("album_id", None) or parsable_url.query.get("id", None)
                assert album_id, parsable_url
                return m.MixiAlbumUrl(parsed_url=parsable_url,
                                      album_id=int(album_id),
                                      owner_id=int(parsable_url.query["owner_id"]))

            # http://mixi.jp/view_album_photo.pl?album_id=149089&owner_id=161740&number=1104680714
            case "view_album_photo.pl", :
                # the number means nothing
                return UnsupportedUrl(parsed_url=parsable_url)

            # https://photo.mixi.jp/view_photo.pl?photo_id=2354695770&owner_id=161740
            case "view_photo.pl", :
                return m.MixiPhotoUrl(parsed_url=parsable_url,
                                      owner_id=int(parsable_url.query["owner_id"]),
                                      photo_id=int(parsable_url.query["photo_id"]))

            # https://photo.mixi.jp/home.pl?owner_id=28854449
            case ("home.pl" | "home.pl#!"), :
                url_query = parsable_url.query.copy()
                url_query.pop("guid", None)
                url_query.pop("from", None)

                if owner_id := url_query.get("owner_id", "").strip("/"):
                    return m.MixiProfileUrl(parsed_url=parsable_url, profile_id=int(owner_id))
                elif not url_query:
                    return UselessUrl(parsed_url=parsable_url)
                else:
                    return None

            # https://video.mixi.jp/list_video.pl?id=730282
            case "list_video.pl", if parsable_url.subdomain == "video":
                if video_id := parsable_url.query.get("id", "").strip("/"):
                    return m.MixiVideoUrl(parsed_url=parsable_url, video_id=int(video_id))
                elif owner_id := parsable_url.query.get("owner_id", ""):
                    return m.MixiProfileUrl(parsed_url=parsable_url, profile_id=int(owner_id))
                else:
                    return None

            # http://mixi.jp/view_community.pl?id=1958589
            case "view_community.pl", :
                return m.MixiCommunityUrl(parsed_url=parsable_url, community_id=int(parsable_url.query["id"].strip("/")))

            # https://mixi.jp/view_bbs.pl?id=84865022&comm_id=1379510
            case "view_bbs.pl", :
                return m.MixiCommunityPostUrl(parsed_url=parsable_url,
                                              community_id=int(parsable_url.query["comm_id"]),
                                              post_id=int(parsable_url.query["id"]))

            # http://mixi.jp/run_appli.pl?id=3774&owner_id=1078055
            case "run_appli.pl", :
                return m.MixiApplicationUrl(parsed_url=parsable_url,
                                            application_id=int(parsable_url.query["id"]),
                                            owner_id=int(parsable_url.query["owner_id"]))

            # http://page.mixi.jp/view_page.pl?page_id=74113
            case _ if parsable_url.subdomain == "page":
                return m.MixiPageUrl(parsed_url=parsable_url,
                                     page_id=int(parsable_url.query["page_id"].strip("/")))

            # http://open.mixi.jp/user/1105979/diary/1967636848
            case "user", user_id, "diary", diary_id:
                return m.MixiDiaryUrl(parsed_url=parsable_url,
                                      diary_id=int(diary_id),
                                      owner_id=int(user_id))

            # http://open.mixi.jp/user/1105979/diary
            case "user", user_id, "diary":
                return m.MixiProfileUrl(parsed_url=parsable_url, profile_id=int(user_id))

            # http://mixi.jp/view_diary.pl?id=237180079&owner_id=3295441
            case "view_diary.pl", :
                return m.MixiDiaryUrl(parsed_url=parsable_url,
                                      diary_id=int(parsable_url.query["id"]),
                                      owner_id=int(parsable_url.query["owner_id"].strip("/")))

            # http://id.mixi.jp/35830124
            case owner_id, if parsable_url.subdomain == "id":
                return m.MixiProfileUrl(parsed_url=parsable_url, profile_id=int(owner_id))

            # http://img1.mixi.jp/photo/bbs_comm/15/48/30821548_123.jpg
            # http://ic.mixi.jp/p/fb7bc5b6e59094d90bcbcdbed9ef70e9039d8c80ae/57106e15/diary/1947224155_249.jpg
            # http://ic69.mixi.jp/p/ce4c304be73b17c22117abd798d51d415569b4e6e0/471baf00/bbs_comm/77/45/299837745_72.jpg
            # http://ic.photo.mixi.jp/v/8b89b48b9ecb552954772b33d3efe04ecae1c4bb10/50cd1465/picture/10693029_1329408778_1large.jpg
            case _ if re.match(r"^(?:ic|img)(?:\d*|\.photo)$", parsable_url.subdomain):
                return m.MixiImageUrl(parsed_url=parsable_url)

            case "login.pl", :
                return cls.match_url(ParsableUrl(parsable_url.query["next_url"]))

            case _:
                return None
