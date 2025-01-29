import pytest

from danboorutools.logical.urls.patreon import PatreonArtistUrl, PatreonGalleryImageUrl, PatreonImageUrl, PatreonPostUrl
from tests.helpers.parsing import generate_parsing_test
from tests.helpers.scraping import _TestArtistUrl, _TestPostUrl

urls = {
    PatreonArtistUrl: {
        "https://www.patreon.com/oughta/posts": "https://www.patreon.com/oughta",
        "http://www.patreon.com/koshio/": "https://www.patreon.com/koshio",
        "https://www.patreon.com/Sirk/creators": "https://www.patreon.com/Sirk",
        "https://www.patreon.com/user?u=4993143": "https://www.patreon.com/user?u=4993143",
        "https://www.patreon.com/m/Alamander820": "https://www.patreon.com/Alamander820",
        "https://www.patreon.com/join/thirdphp?": "https://www.patreon.com/thirdphp",
        "https://patreon.com/checkout/roxxxan?rid=5965351": "https://www.patreon.com/roxxxan",
        "https://www.patreon.com/c/Miyakonoh": "https://www.patreon.com/Miyakonoh",
    },
    PatreonPostUrl: {
        "https://patreon.com/posts/22819080": "https://www.patreon.com/posts/22819080",
        "https://www.patreon.com/posts/nino-13608041": "https://www.patreon.com/posts/nino-13608041",
        "https://www.patreon.com/join/lindaroze/checkout?rid=318429\u0026redirect_uri=%2Fposts%2Fpapi-and-suu-28718113": "https://www.patreon.com/posts/papi-and-suu-28718113",
        "https://www.patreon.com/bePatron?c=170214\u0026rid=218676\u0026redirect_uri=/posts/makoto-nanaya-8366347": "https://www.patreon.com/posts/makoto-nanaya-8366347",
    },
    PatreonImageUrl: {
        "https://cdn3.patreon.com/1/patreon.posts/8488601187679302177.jpg?v=3JKW77OaAo4mC9Tak_CnHRb1MR4-sz0fMaTQRLhlajY%3D": "https://cdn3.patreon.com/1/patreon.posts/8488601187679302177.jpg?v=3JKW77OaAo4mC9Tak_CnHRb1MR4-sz0fMaTQRLhlajY%3D",
        "https://c3.patreon.com/2/patreon-posts/2475253990789383424.png?t=1498176000\u0026v=MwaSWLQaHk67s25L9kOPZwTMeyhxnuNVXFqOBIQWuXA%3D": "https://c3.patreon.com/2/patreon-posts/2475253990789383424.png?t=1498176000\u0026v=MwaSWLQaHk67s25L9kOPZwTMeyhxnuNVXFqOBIQWuXA%3D",
        "https://c10.patreon.com/3/e30%3D/patreon-posts/3L5OtwNuetsk4HajgipG91z7_d-5wAn07awsvd9yJWjAI4_O4ghzS90k2OSfiqCA.jpg?token-time=1502409600\u0026token-hash=aHjY4qz5GqNu3sQ5_AAHa3vApAsEfMCRi_Agxi5I1sM%3D": "https://c10.patreon.com/3/e30%3D/patreon-posts/3L5OtwNuetsk4HajgipG91z7_d-5wAn07awsvd9yJWjAI4_O4ghzS90k2OSfiqCA.jpg?token-time=1502409600\u0026token-hash=aHjY4qz5GqNu3sQ5_AAHa3vApAsEfMCRi_Agxi5I1sM%3D",
        "https://c3.patreon.com/2/patreon.user/Xw9EBuJAeV0Xh360JZzYT1KaQx1svrgqL9AfIx9ZVhHSRTEJmMyqGHu5l26Jazsw_large_2.png?t=1494853451\u0026w=1920\u0026v=qXwa0ugy4NEFLvLMNPa4421H44YdNXni5Ur1HcIU3d4%3D": "https://c3.patreon.com/2/patreon.user/Xw9EBuJAeV0Xh360JZzYT1KaQx1svrgqL9AfIx9ZVhHSRTEJmMyqGHu5l26Jazsw_large_2.png?t=1494853451\u0026w=1920\u0026v=qXwa0ugy4NEFLvLMNPa4421H44YdNXni5Ur1HcIU3d4%3D",
        "https://c10.patreonusercontent.com/3/eyJ3Ijo2MjB9/patreon-media/p/post/36495392/cb0702f66b4945d5adaf3fcd98d0f077/1.jpg?token-time=1591617419\u0026token-hash=C9E0pBzAiL4iKHiRhv98Otv2rXfd0ay5-hSGp6ahdZ8=": "https://c10.patreonusercontent.com/3/eyJ3Ijo2MjB9/patreon-media/p/post/36495392/cb0702f66b4945d5adaf3fcd98d0f077/1.jpg?token-time=1591617419\u0026token-hash=C9E0pBzAiL4iKHiRhv98Otv2rXfd0ay5-hSGp6ahdZ8=",
        "https://c10.patreonusercontent.com/3/e30%3D/patreon-posts/o2-s3ubiq-rvQgJVTMlI4-_djsAXvF_YiV2LSEKkpv9sTxqhDKo9-WboTju_sjTU.png?token-time=1506470400\u0026token-hash=htqRR_7JryCMoDqgyknNFqfRWrejuahP16JKwWnaUrA%3D": "https://c10.patreonusercontent.com/3/e30%3D/patreon-posts/o2-s3ubiq-rvQgJVTMlI4-_djsAXvF_YiV2LSEKkpv9sTxqhDKo9-WboTju_sjTU.png?token-time=1506470400\u0026token-hash=htqRR_7JryCMoDqgyknNFqfRWrejuahP16JKwWnaUrA%3D",
        "https://c10.patreonusercontent.com/4/patreon-media/p/post/73164326/0b437130a504407e9cddbe57b575f4d0/eyJxIjoxMDAsIndlYnAiOjB9/1.png?token-time=1668729600\u0026token-hash=cRKqb666VduPfE04ZnUQYOwkl8gWcfcJakWMrqHCUOI=": "https://c10.patreonusercontent.com/4/patreon-media/p/post/73164326/0b437130a504407e9cddbe57b575f4d0/eyJxIjoxMDAsIndlYnAiOjB9/1.png?token-time=1668729600\u0026token-hash=cRKqb666VduPfE04ZnUQYOwkl8gWcfcJakWMrqHCUOI=",
        "https://www.patreon.com/file?h=77985451&i=12964662": "https://www.patreon.com/file?h=77985451&i=12964662",
    },
    PatreonGalleryImageUrl: {
        "https://c10.patreonusercontent.com/4/patreon-media/p/reward/5965351/d0735f0547ac45d09bcf7dda9abf9380/eyJ3Ijo0MDB9/5.png?token-time=2145916800&token-hash=a_2MAWOmMGh9WiqG6hSmvPdlM954Px0UtvWB_HbqQjg%3D": "https://c10.patreonusercontent.com/4/patreon-media/p/reward/5965351/d0735f0547ac45d09bcf7dda9abf9380/eyJ3Ijo0MDB9/5.png?token-time=2145916800&token-hash=a_2MAWOmMGh9WiqG6hSmvPdlM954Px0UtvWB_HbqQjg%3D",
        "https://c10.patreonusercontent.com/4/patreon-media/p/campaign/5313652/bf5316fcf0474739a2b5c846d9d21d89/eyJxIjoxMDAsIndlYnAiOjB9/4.png?token-time=1708300800&token-hash=SZ76Gqg5BEz2PKpUNbRfuPoARGIOYMdhQePXytxmUSo%3D": "https://c10.patreonusercontent.com/4/patreon-media/p/campaign/5313652/bf5316fcf0474739a2b5c846d9d21d89/eyJxIjoxMDAsIndlYnAiOjB9/4.png?token-time=1708300800&token-hash=SZ76Gqg5BEz2PKpUNbRfuPoARGIOYMdhQePXytxmUSo%3D",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)


class TestPatreonArtistUrl1(_TestArtistUrl):
    url_string = "https://www.patreon.com/himetyanart"
    url_type = PatreonArtistUrl
    url_properties = dict(username="himetyanart")
    primary_names = ["Hime-Tyan Art"]
    secondary_names = ["himetyanart"]
    related = [
        "https://www.instagram.com/tyanka6",
        "https://twitter.com/Antyan87884404",
    ]
    assets = [
        "https://c10.patreonusercontent.com/4/patreon-media/p/reward/3801428/d034197039534b209fcba2c405159332/eyJ3Ijo0MDB9/2.jpg?token-time=2145916800&token-hash=APzkJ2A-hQ8vdtiOExO1_jVK3fMHflAdiLDxg3OiGJ0%3D",
        "https://c10.patreonusercontent.com/4/patreon-media/p/reward/3801432/a706ca3033fc49c68c87763544c24526/eyJ3Ijo0MDB9/2.jpg?token-time=2145916800&token-hash=6JCvaY7UnIItugsF-NFrIc90Ljk4DGqAOXYsvsP4eEo%3D",
        "https://c10.patreonusercontent.com/4/patreon-media/p/reward/10203828/af13b13a1fa6442f9204d6b7b93371d2/eyJ3Ijo0MDB9/1.jpeg?token-time=2145916800&token-hash=Bujg4Zr2yGyD-9-yTcY7SfcPdYZVlry5F7HNe3bmdBo%3D",
    ]


class TestPatreonArtistUrl2(_TestArtistUrl):
    url_string = "https://www.patreon.com/teiputi"
    url_type = PatreonArtistUrl
    url_properties = dict(username="teiputi")
    primary_names = []
    secondary_names = ["teiputi"]
    related = []
    is_deleted = True


class TestPatreonArtistUrl3(_TestArtistUrl):
    url_string = "https://www.patreon.com/kuro_gane"
    url_type = PatreonArtistUrl
    url_properties = dict(username="kuro_gane")
    primary_names = []
    secondary_names = ["kuro_gane"]
    related = []
    is_deleted = True


class TestPatreonPostUrl(_TestPostUrl):
    url_string = "https://www.patreon.com/posts/wu-xiu-zheng-ku-92745989"
    url_type = PatreonPostUrl
    url_properties = dict(post_id=92745989, title="wu-xiu-zheng-ku", username=None)
    gallery = "https://www.patreon.com/TakaneNTR"
