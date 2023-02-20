from danboorutools.logical.extractors.nijie import NijieImageUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class NijieNetParser(UrlParser):
    test_cases = {
        NijieImageUrl: [
            "https://pic.nijie.net/07/nijie/17/95/728995/illust/0_0_403fdd541191110c_c25585.jpg",
            "https://pic.nijie.net/06/nijie/17/14/236014/illust/218856_1_7646cf57f6f1c695_f2ed81.png",
            "https://pic.nijie.net/03/nijie_picture/236014_20170620101426_0.png",  # (page: https://www.nijie.info/view.php?id=218856)
            "https://pic.nijie.net/01/nijie_picture/diff/main/196201_20150201033106_0.jpg",
            "http://pic.nijie.net/01/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg (NSFW)",
            "http://pic.nijie.net/01/__rs_l120x120/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg",
            "https://pic.nijie.net/02/nijie/15/46/3846/illust/110835_0_e4f46a73bd61a738_421472.jpg",
            "https://pic.nijie.net/04/nijie/14/36/13836/illust/107712_0_3152831264061229_e9b955.jpg",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> NijieImageUrl | None:
        match parsable_url.url_parts:
            case _, "nijie_picture", *_, filename:
                instance = NijieImageUrl(parsable_url)
                instance.parse_filename(filename)

            case *_, "dojin_main", "dojin_sam", _:  # jackshit
                instance = NijieImageUrl(parsable_url)
                instance.post_id = None
                instance.page = None
                instance.user_id = None

            case _, "nijie", _, _, user_id, "illust", filename:
                instance = NijieImageUrl(parsable_url)
                instance.parse_filename(filename)
                instance.user_id = int(user_id)

            case _:
                return None

        return instance
