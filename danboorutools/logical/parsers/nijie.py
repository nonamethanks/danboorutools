from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.extractors.nijie import NijieArtistUrl, NijieImageUrl, NijiePostUrl, NijieUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NijieInfoParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> NijieUrl | None:
        instance: NijieUrl
        match parsable_url.url_parts:
            # https://nijie.info/members.php?id=236014
            # https://nijie.info/members_illust.php?id=236014
            case ("members.php" | "members_illust.php"), :
                instance = NijieArtistUrl(parsable_url)
                instance.user_id = int(parsable_url.query["id"])

            # https://nijie.info/view.php?id=167755
            # https://nijie.info/view.php?id=218856
            # https://www.nijie.info/view.php?id=218856
            # https://sp.nijie.info/view.php?id=218856
            case "view.php", :
                instance = NijiePostUrl(parsable_url)
                instance.post_id = int(parsable_url.query["id"])

            # https://nijie.info/view_popup.php?id=218856#diff_1  # starts from 0
            # https://sp.nijie.info/view_popup.php?id=476470#popup_illust_3  # starts from 1
            # https://nijie.info/view_popup.php?id=218856
            case "view_popup.php", :
                instance = NijieImageUrl(parsable_url)
                if "#" in parsable_url.query["id"]:
                    post_id, page = parsable_url.query["id"].split("#")
                    if page.startswith("diff_"):
                        instance.page = int(page.removeprefix("diff_"))
                    elif page.startswith("popup_illust_"):
                        instance.page = int(page.removeprefix("popup_illust_")) - 1
                    else:
                        raise NotImplementedError(parsable_url.query["id"])
                else:
                    post_id = parsable_url.query["id"]
                    instance.page = 0
                instance.post_id = int(post_id)
                instance.user_id = None

            # https://pic01.nijie.info/nijie_picture/diff/main/218856_0_236014_20170620101329.png
            # https://pic01.nijie.info/nijie_picture/diff/main/218856_1_236014_20170620101330.png
            # https://pic05.nijie.info/nijie_picture/diff/main/559053_20180604023346_1.png
            # https://pic04.nijie.info/nijie_picture/diff/main/287736_161475_20181112032855_1.png
            # https://pic03.nijie.info/nijie_picture/28310_20131101215959.jpg
            # https://pic03.nijie.info/nijie_picture/236014_20170620101426_0.png
            # http://pic01.nijie.info/nijie_picture/20120615025744927.jpg
            case "nijie_picture", *_, filename:
                instance = NijieImageUrl(parsable_url)
                instance.parse_filename(filename)

            # http://nijie.info/media/nijietan.swf
            case "media", _:
                raise UnparsableUrlError(parsable_url)

            case _:
                return None

        return instance


class NijieNetParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> NijieImageUrl | None:
        match parsable_url.url_parts:
            # https://pic.nijie.net/03/nijie_picture/236014_20170620101426_0.png  # (page: https://www.nijie.info/view.php?id=218856)
            # https://pic.nijie.net/01/nijie_picture/diff/main/196201_20150201033106_0.jpg
            case _, "nijie_picture", *_, filename:
                instance = NijieImageUrl(parsable_url)
                instance.parse_filename(filename)

            # http://pic.nijie.net/01/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg
            # http://pic.nijie.net/01/__rs_l120x120/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg
            case *_, "dojin_main", "dojin_sam", _:  # jackshit
                instance = NijieImageUrl(parsable_url)
                instance.post_id = None
                instance.page = None
                instance.user_id = None

            # https://pic.nijie.net/07/nijie/17/95/728995/illust/0_0_403fdd541191110c_c25585.jpg
            # https://pic.nijie.net/06/nijie/17/14/236014/illust/218856_1_7646cf57f6f1c695_f2ed81.png
            # https://pic.nijie.net/02/nijie/15/46/3846/illust/110835_0_e4f46a73bd61a738_421472.jpg
            # https://pic.nijie.net/04/nijie/14/36/13836/illust/107712_0_3152831264061229_e9b955.jpg
            case _, "nijie", _, _, user_id, "illust", filename:
                instance = NijieImageUrl(parsable_url)
                instance.parse_filename(filename)
                instance.user_id = int(user_id)

            case _:
                return None

        return instance
