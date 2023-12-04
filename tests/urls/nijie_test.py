import pytest

from danboorutools.logical.urls.nijie import NijieArtistUrl, NijieImageUrl, NijiePostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import generate_artist_test

urls = {
    NijieArtistUrl: {
        "https://nijie.info/members.php?id=236014": "https://nijie.info/members.php?id=236014",
        "https://nijie.info/members_illust.php?id=236014": "https://nijie.info/members.php?id=236014",
    },
    NijieImageUrl: {
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

        "https://pic.nijie.net/07/nijie/17/95/728995/illust/0_0_403fdd541191110c_c25585.jpg": "https://pic.nijie.net/07/nijie/17/95/728995/illust/0_0_403fdd541191110c_c25585.jpg",
        "https://pic.nijie.net/06/nijie/17/14/236014/illust/218856_1_7646cf57f6f1c695_f2ed81.png": "https://pic.nijie.net/06/nijie/17/14/236014/illust/218856_1_7646cf57f6f1c695_f2ed81.png",
        "https://pic.nijie.net/03/nijie_picture/236014_20170620101426_0.png": "https://pic.nijie.net/03/nijie_picture/236014_20170620101426_0.png",
        "https://pic.nijie.net/01/nijie_picture/diff/main/196201_20150201033106_0.jpg": "https://pic.nijie.net/01/nijie_picture/diff/main/196201_20150201033106_0.jpg",
        "http://pic.nijie.net/01/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg (NSFW)": "https://pic.nijie.net/01/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg (NSFW)",
        "http://pic.nijie.net/01/__rs_l120x120/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg": "https://pic.nijie.net/01/dojin_main/dojin_sam/20120213044700コピー ～ 0011のコピー.jpg",
        "https://pic.nijie.net/02/nijie/15/46/3846/illust/110835_0_e4f46a73bd61a738_421472.jpg": "https://pic.nijie.net/02/nijie/15/46/3846/illust/110835_0_e4f46a73bd61a738_421472.jpg",
        "https://pic.nijie.net/04/nijie/14/36/13836/illust/107712_0_3152831264061229_e9b955.jpg": "https://pic.nijie.net/04/nijie/14/36/13836/illust/107712_0_3152831264061229_e9b955.jpg",
        "https://pic.nijie.net/02/__rs_l120x120/nijie/23m03/71/23671/illust/547821_0_d9b4b00e9b8ea900_e0f435.png": "https://pic.nijie.net/02/nijie/23m03/71/23671/illust/547821_0_d9b4b00e9b8ea900_e0f435.png",

    },
    NijiePostUrl: {
        "https://nijie.info/view.php?id=167755": "https://nijie.info/view.php?id=167755",
        "https://nijie.info/view.php?id=218856": "https://nijie.info/view.php?id=218856",
        "https://www.nijie.info/view.php?id=218856": "https://nijie.info/view.php?id=218856",
        "https://sp.nijie.info/view.php?id=218856": "https://nijie.info/view.php?id=218856",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


def test_artist_url_1():
    generate_artist_test(
        url_string="https://nijie.info/members.php?id=1149787",
        url_type=NijieArtistUrl,
        url_properties=dict(user_id=1149787),
        primary_names=["れく/れとまクロ：仕事求ム！"],
        secondary_names=["nijie_1149787"],
        related=["https://ci-en.dlsite.com/creator/1049",
                 "https://skeb.jp/@rexpace",
                 "https://www.dmm.co.jp/dc/doujin/-/list/=/article=maker/id=76572/",
                 "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG16604.html",
                 "http://twitter.com/rexpace",
                 "https://t.co/Lf7P5sOLdV"],
    )
