from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.nijie import NijieArtistUrl, NijieImageUrl, NijiePostUrl, NijieUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NijieInfoParser(UrlParser):
    test_cases = {
        NijieArtistUrl: [
            "https://nijie.info/members.php?id=236014",
            "https://nijie.info/members_illust.php?id=236014",
        ],
        NijieImageUrl: [
            "https://pic01.nijie.info/nijie_picture/diff/main/218856_0_236014_20170620101329.png",
            "https://pic01.nijie.info/nijie_picture/diff/main/218856_1_236014_20170620101330.png",
            "https://pic05.nijie.info/nijie_picture/diff/main/559053_20180604023346_1.png",
            "https://pic04.nijie.info/nijie_picture/diff/main/287736_161475_20181112032855_1.png",
            "https://pic03.nijie.info/nijie_picture/28310_20131101215959.jpg",
            "https://pic03.nijie.info/nijie_picture/236014_20170620101426_0.png",
            "http://pic01.nijie.info/nijie_picture/20120615025744927.jpg",
            "https://nijie.info/view_popup.php?id=218856#diff_1",  # starts from 0
            "https://sp.nijie.info/view_popup.php?id=476470#popup_illust_3",  # starts from 1
            "https://nijie.info/view_popup.php?id=218856",
        ],
        NijiePostUrl: [
            "https://nijie.info/view.php?id=167755",  # (deleted post)
            "https://nijie.info/view.php?id=218856",
            "https://www.nijie.info/view.php?id=218856",
            "https://sp.nijie.info/view.php?id=218856",

        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> NijieUrl | None:
        instance: NijieUrl
        match parsable_url.url_parts:
            case ("members.php" | "members_illust.php"), :
                instance = NijieArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.params["id"])
            case "view.php", :
                instance = NijiePostUrl(parsable_url)
                instance.post_id = int(parsable_url.params["id"])
            case "view_popup.php", :
                instance = NijieImageUrl(parsable_url)
                if "#" in parsable_url.params["id"]:
                    post_id, page = parsable_url.params["id"].split("#")
                    if page.startswith("diff_"):
                        instance.page = int(page.removeprefix("diff_"))
                    elif page.startswith("popup_illust_"):
                        instance.page = int(page.removeprefix("popup_illust_")) - 1
                    else:
                        raise NotImplementedError(parsable_url.params["id"])
                else:
                    post_id = parsable_url.params["id"]
                    instance.page = 0
                instance.post_id = int(post_id)
                instance.user_id = None
            case "nijie_picture", *_, filename:
                instance = NijieImageUrl(parsable_url)
                instance.parse_filename(filename)

            # http://nijie.info/media/nijietan.swf
            case "media", _:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance
