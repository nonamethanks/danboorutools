from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import facebook as fb
from danboorutools.models.url import UselessUrl


class FacebookComParser(UrlParser):
    RESERVED_NAMES = ("home", "help", "timeline", "pages", "groups", "people", "pg", "photos", "posts", "about", "media", "videos")

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> fb.FacebookUrl | UselessUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://www.facebook.com/annamakkotan/posts/676864725988821/
            # https://www.facebook.com/fkscrashing/posts/pfbid02DGobMuY9xXcdnitCwBQxAL6hXBgATLMprXdU4afdoTabjvULYj9LLQRxFmdCcW3Yl
            case username, "posts", post_id:
                return fb.FacebookPostUrl(parsed_url=parsable_url,
                                          post_id=post_id,
                                          username=username)

            # https://www.facebook.com/people/%E3%82%AD%E3%83%A7%E3%83%B3%E5%AD%90%E3%81%A8%E3%81%8B-%E8%89%B2%E3%80%85/pfbid0XPSTMTjqzUCw6JhKZxzd4NPtqoaVRzJWs1NDKWRpENNNDjEm6gQ3fBjKFSvSh42Sl/
            # https://www.facebook.com/people/Lydia-QX/100007225127583
            case "people", people_name, people_id:
                return fb.FacebookPeopleUrl(parsed_url=parsable_url,
                                            people_name=people_name,
                                            people_id=people_id)

            # https://www.facebook.com/comaofsoulsart/photos/a.1533192583644740.1073741828.1533190756978256/1564060640557934/?type=3\u0026theater
            # https://www.facebook.com/WangphingStudios/photos/pb.370544529763924.-2207520000.1457686688./592710564213985/?type=3\u0026theater
            # https://www.facebook.com/WangphingStudios/photos/592710564213985/
            # https://www.facebook.com/TypeMoonWorld/photos/pcb.3060422600867484/3060422470867497/?type=3&theater
            # https://www.facebook.com/BoltertoKokoro/photos/a.1329829920487418/1470977829705959/?type=3://scontent.fbwn1-1.fna.fbcdn.net/v/t1.0-9/60859695_1470977833039292_7758017375433129984_n.jpg?_nc_cat=103\u0026_nc_ht=scontent.fbwn1-1.fna\u0026oh=da6331cbe01e7adf90381f7f42a46ef6\u0026oe=5D5268E9
            case username, "photos", _, post_id:
                return fb.FacebookPostUrl(parsed_url=parsable_url,
                                          post_id=post_id,
                                          username=username)

            # https://www.facebook.com/TypeMoonWorld/photos/3060422500867494
            # https://www.facebook.com/TypeMoonWorld/posts/3060422500867494
            case username, ("photos" | "posts" | "videos"), post_id:
                return fb.FacebookPostUrl(parsed_url=parsable_url,
                                          post_id=post_id,
                                          username=username)

            # https://m.facebook.com/global.honkaiimpact/posts/wallpaper-honkai-quest-wallpaper-selection-click-the-link-using-pc-to-download-t/695401147785427/
            case username, ("posts" | "videos"), _, post_id if post_id.isnumeric():
                return fb.FacebookPostUrl(parsed_url=parsable_url,
                                          post_id=post_id,
                                          username=username)

            # https://www.facebook.com/groups/384769965268215/
            # https://www.facebook.com/groups/156152374985181/user/100000607292435/
            # https://www.facebook.com/groups/corvitarts
            case "groups", group_id, *_:
                return fb.FacebookGroupUrl(parsed_url=parsable_url,
                                           group_id=group_id)

            # https://www.facebook.com/pages/category/Artist/Keith-Byrne-Art-243104839060471/
            case "pages", "category", category, old_id:
                return fb.FacebookOldPageUrl(parsed_url=parsable_url,
                                             old_id=old_id,
                                             category=category)

            # https://www.facebook.com/pages/Maku-Zoku/212126028816287
            case "pages", page_name, page_id:
                return fb.FacebookPageUrl(parsed_url=parsable_url,
                                          page_name=page_name,
                                          page_id=int(page_id))

            case "pages", _:  # broken urls, they don't redirect
                raise UnparsableUrlError(parsable_url)

            # https://www.facebook.com/pg/lanbow2000/photos/?tab=album\u0026album_id=376505442485366
            # https://www.facebook.com/pg/AzizDraws/posts/
            case "pg", username, subdir if subdir in cls.RESERVED_NAMES:
                return fb.FacebookUserUrl(parsed_url=parsable_url,
                                          username=username)

            # https://www.facebook.com/pg/chocokangoo
            case "pg", username:
                return fb.FacebookUserUrl(parsed_url=parsable_url,
                                          username=username)

            # https://www.facebook.com/The-Art-of-Ken-Barthelmey-229517583791109/timeline/
            # https://www.facebook.com/bladencreator/about/
            # https://www.facebook.com/SuperMechaChampionsGlobal/photos/
            case username, subdir if subdir in cls.RESERVED_NAMES:
                return fb.FacebookUserUrl(parsed_url=parsable_url, username=username)

            case "profile.php", :
                return fb.FacebookOldPeopleUrl(parsed_url=parsable_url, people_id=parsable_url.query["id"])

            # https://www.facebook.com/KittyRaymson/
            case username, if username not in cls.RESERVED_NAMES:
                return fb.FacebookUserUrl(parsed_url=parsable_url,
                                          username=username)

            case subdir, if subdir in cls.RESERVED_NAMES:
                return UselessUrl(parsed_url=parsable_url)

            # https://www.facebook.com/media/set/?set=a.1972049129486802
            case "media", "set":
                return fb.FacebookMediaSetUrl(parsed_url=parsable_url,
                                              media_set_id=parsable_url.query["set"])

            case "cds.sg", _:
                raise UnparsableUrlError(parsable_url)  # game url???

            case _:
                return None
