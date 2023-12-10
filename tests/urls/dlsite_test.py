import pytest

from danboorutools.logical.urls.dlsite import DlsiteAuthorUrl, DlsiteImageUrl, DlsiteWorkUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestPostUrl

urls = {
    DlsiteAuthorUrl: {
        "https://www.dlsite.com/books/author/=/author_id/AJ002787": "https://www.dlsite.com/books/author/=/author_id/AJ002787",
        "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG28852.html": "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG28852",
        "https://www.dlsite.com/ecchi-eng/circle/profile/=/maker_id/RG12762.html": "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG12762",
        "https://www.dlsite.com/girls/circle/profile/=/maker_id/RG67968.html": "https://www.dlsite.com/girls/circle/profile/=/maker_id/RG67968",
        "https://www.dlsite.com/bl/circle/profile/=/maker_id/RG58534.html": "https://www.dlsite.com/bl/circle/profile/=/maker_id/RG58534",
        "http://www.dlsite.com/home/circle/profile/=/maker_id/RG27185.html": "https://www.dlsite.com/home/circle/profile/=/maker_id/RG27185",
        "https://www.dlsite.com/eng/circle/profile/=/maker_id/RG24167.html": "https://www.dlsite.com/home/circle/profile/=/maker_id/RG24167",
        "http://maniax.dlsite.com/circle/profile/=/maker_id/RG12065.html": "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG12065",
        "http://www.dlsite.com/pro/circle/profile/=/maker_id/VG01352.html": "https://www.dlsite.com/pro/circle/profile/=/maker_id/VG01352",
        "http://maniax.dlsite.com/fsr/=/kw/RG06677/od/reg_d": "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG06677",
        "https://www.dlsite.com/maniax/fsr/=/kw/RG06677/od/reg_d": "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG06677",
        "http://www.dlsite.com/books/fsr/=/keyword_maker_name/丹羽香ゆあん+AJ003398/": "https://www.dlsite.com/books/author/=/author_id/AJ003398",
        "http://www.dlsite.com/books/fsr/=/keyword_maker_name/AJ005866/": "https://www.dlsite.com/books/author/=/author_id/AJ005866",
        "http://www.dlsite.com/books/fsr/=/keyword_maker_name/%BF%DC%C6%A3%A4%EB%A4%AF%20AJ001613/from/work.author": "https://www.dlsite.com/books/author/=/author_id/AJ001613",
        "http://www.dlsite.com/books/fsr/=/keyword_maker_name/%B8%A4%C0%B1%20AJ002493": "https://www.dlsite.com/books/author/=/author_id/AJ002493",
        "http://www.dlsite.com/gay/circle/profile/=/maker_id/RG13474.html": "https://www.dlsite.com/bl/circle/profile/=/maker_id/RG13474",
        "http://www.dlsite.com/gay-touch/circle/profile/=/from/work.maker/maker_id/RG35592.html": "https://www.dlsite.com/bl/circle/profile/=/maker_id/RG35592",
        "https://www.dlsite.com/maniax/fsr/=/kw/RG29700/": "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG29700",
        "http://www.dlsite.com/maniax/fsr/=/keyword_maker_name/空道へのR%20RG25050/ana_flg/all/from/work.same_maker": "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG25050",
        "http://www.dlsite.com/maniax-touch/circle/profile/=/from/work.maker/maker_id/RG36965.html": "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG36965",
        "https://www.dlsite.com/maniax/dlaf/=/link/profile/aid/sotokanda/maker/RG03905.html": "https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG03905",
    },
    DlsiteWorkUrl: {
        "https://www.dlsite.com/books/work/=/product_id/BJ115183": "https://www.dlsite.com/books/work/=/product_id/BJ115183",
        "https://www.dlsite.com/girls/work/=/product_id/RJ01023665.html": "https://www.dlsite.com/girls/work/=/product_id/RJ01023665",
        "https://www.dlsite.com/bl/work/=/product_id/RJ01013942.html": "https://www.dlsite.com/bl/work/=/product_id/RJ01013942",
        "http://maniax.dlsite.com/work/=/product_id/RJ065490.html": "https://www.dlsite.com/maniax/work/=/product_id/RJ065490",
        "http://dlsite.jp/mawtw/RJ198108": "https://www.dlsite.com/maniax/work/=/product_id/RJ198108",
        "http://dlsite.jp/howtw/RJ219372": "https://www.dlsite.com/home/work/=/product_id/RJ219372",
        "http://www.dlsite.com/maniax/dlaf/=/link/work/aid/tbnb/id/RJ109634.html": "https://www.dlsite.com/maniax/work/=/product_id/RJ109634",
        "https://www.dlsite.com/maniax/dlaf/=/t/s/link/work/aid/yuen/locale/en_US/id/RJ326899.html/?locale=en_US": "https://www.dlsite.com/maniax/work/=/product_id/RJ326899",
        "http://home.dlsite.com/dlaf/=/aid/iisearch/url/http%253A%252F%252Fmaniax.dlsite.com%252Fwork%252F%253D%252Fproduct_id%252FRJ034344.html": "https://www.dlsite.com/maniax/work/=/product_id/RJ034344",
        "http://maniax.dlsite.com/work/=/product_site/1/product_id/RJ025429.html": "https://www.dlsite.com/maniax/work/=/product_id/RJ025429",
    },
    DlsiteImageUrl: {
        "https://img.dlsite.jp/resize/images2/work/books/BJ007000/BJ006925_img_main_240x240.jpg": "https://img.dlsite.jp/modpub/images2/work/books/BJ007000/BJ006925_img_main.jpg",
        "https://img.dlsite.jp/modpub/images2/work/books/BJ007000/BJ006925_img_main.jpg": "https://img.dlsite.jp/modpub/images2/work/books/BJ007000/BJ006925_img_main.jpg",
        "https://img.dlsite.jp/modpub/images2/work/books/BJ007000/BJ006925_img_main.webp": "https://img.dlsite.jp/modpub/images2/work/books/BJ007000/BJ006925_img_main.jpg",
        "https://img.dlsite.jp/modpub/images2/work/books/BJ007000/BJ006925_img_smp1.jpg": "https://img.dlsite.jp/modpub/images2/work/books/BJ007000/BJ006925_img_smp1.jpg",
        "https://img.dlsite.jp/resize/images2/work/doujin/RJ01014000/RJ01013942_img_main_240x240.jpg": "https://img.dlsite.jp/modpub/images2/work/doujin/RJ01014000/RJ01013942_img_main.jpg",
        "https://img.dlsite.jp/modpub/images2/ana/doujin/RJ181000/RJ180508_ana_img_main.webp": "https://img.dlsite.jp/modpub/images2/ana/doujin/RJ181000/RJ180508_ana_img_main.jpg",
        "http://maniax.dlsite.com/modpub/images2/work/doujin/RJ032000/RJ031102_img_smp1.jpg": "http://maniax.dlsite.com/modpub/images2/work/doujin/RJ032000/RJ031102_img_smp1.jpg",
        "https://img.dlsite.jp/modpub/images2/parts/RJ278000/RJ277383/RJ277383_PTS0000021229_0.jpg": "https://img.dlsite.jp/modpub/images2/parts/RJ278000/RJ277383/RJ277383_PTS0000021229_0.jpg",
        "https://img.dlsite.jp/modpub/images2/parts_ana/RJ339000/RJ338222/0533754c8834945565155e2635c6a349.jpg": "https://img.dlsite.jp/modpub/images2/parts_ana/RJ339000/RJ338222/0533754c8834945565155e2635c6a349.jpg",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestDlsiteWorkUrl(_TestPostUrl):
    url_string = "https://www.dlsite.com/books/work/=/product_id/BJ115183.html/?unique_op=af&utm_medium=affiliate&utm_source=none"
    url_type = DlsiteWorkUrl
    url_properties = dict(work_id="BJ115183", subsite="books")
    gallery = "https://www.dlsite.com/books/author/=/author_id/AJ002787"
