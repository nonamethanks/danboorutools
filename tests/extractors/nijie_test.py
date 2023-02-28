
from ward import test

from danboorutools.models.url import Url

urls = {

    "https://nijie.info/members.php?id=236014": "https://nijie.info/members.php?id=236014",
    "https://nijie.info/members_illust.php?id=236014": "https://nijie.info/members.php?id=236014",

    "https://pic01.nijie.info/nijie_picture/diff/main/218856_0_236014_20170620101329.png": "https://pic01.nijie.info/nijie_picture/diff/main/218856_0_236014_20170620101329.png",
    "https://pic01.nijie.info/nijie_picture/diff/main/218856_1_236014_20170620101330.png": "https://pic01.nijie.info/nijie_picture/diff/main/218856_1_236014_20170620101330.png",
    "https://pic05.nijie.info/nijie_picture/diff/main/559053_20180604023346_1.png": "https://pic05.nijie.info/nijie_picture/diff/main/559053_20180604023346_1.png",
    "https://pic04.nijie.info/nijie_picture/diff/main/287736_161475_20181112032855_1.png": "https://pic04.nijie.info/nijie_picture/diff/main/287736_161475_20181112032855_1.png",
    "https://pic03.nijie.info/nijie_picture/28310_20131101215959.jpg": "https://pic03.nijie.info/nijie_picture/28310_20131101215959.jpg",
    "https://pic03.nijie.info/nijie_picture/236014_20170620101426_0.png": "https://pic03.nijie.info/nijie_picture/236014_20170620101426_0.png",
    "http://pic01.nijie.info/nijie_picture/20120615025744927.jpg": "https://pic01.nijie.info/nijie_picture/20120615025744927.jpg",
    "https://nijie.info/view_popup.php?id=218856#diff_1": "https://nijie.info/view_popup.php?id=218856#diff_1",
    "https://sp.nijie.info/view_popup.php?id=476470#popup_illust_3": "https://nijie.info/view_popup.php?id=476470#diff_2",
    "https://nijie.info/view_popup.php?id=218856": "https://nijie.info/view_popup.php?id=218856",

    "https://nijie.info/view.php?id=167755": "https://nijie.info/view.php?id=167755",
    "https://nijie.info/view.php?id=218856": "https://nijie.info/view.php?id=218856",
    "https://www.nijie.info/view.php?id=218856": "https://nijie.info/view.php?id=218856",
    "https://sp.nijie.info/view.php?id=218856": "https://nijie.info/view.php?id=218856",

    "https://pic.nijie.net/07/nijie/17/95/728995/illust/0_0_403fdd541191110c_c25585.jpg": "https://pic.nijie.net/07/nijie/17/95/728995/illust/0_0_403fdd541191110c_c25585.jpg",
    "https://pic.nijie.net/06/nijie/17/14/236014/illust/218856_1_7646cf57f6f1c695_f2ed81.png": "https://pic.nijie.net/06/nijie/17/14/236014/illust/218856_1_7646cf57f6f1c695_f2ed81.png",
    "https://pic.nijie.net/03/nijie_picture/236014_20170620101426_0.png": "https://pic.nijie.net/03/nijie_picture/236014_20170620101426_0.png",
    "https://pic.nijie.net/01/nijie_picture/diff/main/196201_20150201033106_0.jpg": "https://pic.nijie.net/01/nijie_picture/diff/main/196201_20150201033106_0.jpg",
    "http://pic.nijie.net/01/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg (NSFW)": "https://pic.nijie.net/01/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg (NSFW)",
    "http://pic.nijie.net/01/__rs_l120x120/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg": "https://pic.nijie.net/01/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg",
    "https://pic.nijie.net/02/nijie/15/46/3846/illust/110835_0_e4f46a73bd61a738_421472.jpg": "https://pic.nijie.net/02/nijie/15/46/3846/illust/110835_0_e4f46a73bd61a738_421472.jpg",
    "https://pic.nijie.net/04/nijie/14/36/13836/illust/107712_0_3152831264061229_e9b955.jpg": "https://pic.nijie.net/04/nijie/14/36/13836/illust/107712_0_3152831264061229_e9b955.jpg",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
