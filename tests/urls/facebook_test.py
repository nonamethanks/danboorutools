import pytest

from danboorutools.logical.urls import facebook as fb
from tests.helpers.parsing import generate_parsing_test

urls = {
    fb.FacebookPageUrl: {
        "https://www.facebook.com/pages/Maku-Zoku/212126028816287": "https://www.facebook.com/pages/Maku-Zoku/212126028816287",
    },
    fb.FacebookPeopleUrl: {
        "https://www.facebook.com/people/Lydia-QX/pfbid0qnrntLX3supTYDL6wTZCMwjpSnyDsjdEiiwPu8NG2SzhX1Nf8VfN15gG7jntmne9l/": "https://www.facebook.com/people/Lydia-QX/pfbid0qnrntLX3supTYDL6wTZCMwjpSnyDsjdEiiwPu8NG2SzhX1Nf8VfN15gG7jntmne9l",
    },
    fb.FacebookUserUrl: {
        "https://www.facebook.com/KittyRaymson/": "https://www.facebook.com/KittyRaymson",
        "https://www.facebook.com/pg/chocokangoo": "https://www.facebook.com/chocokangoo",
        "https://www.facebook.com/The-Art-of-Ken-Barthelmey-229517583791109/timeline/": "https://www.facebook.com/The-Art-of-Ken-Barthelmey-229517583791109",
        "https://www.facebook.com/pg/lanbow2000/photos/?tab=album\u0026album_id=376505442485366": "https://www.facebook.com/lanbow2000",
        "https://www.facebook.com/pg/AzizDraws/posts/": "https://www.facebook.com/AzizDraws",
        "https://www.facebook.com/bladencreator/about/": "https://www.facebook.com/bladencreator",
    },
    fb.FacebookGroupUrl: {
        "https://www.facebook.com/groups/384769965268215/": "https://www.facebook.com/groups/384769965268215",
        "https://www.facebook.com/groups/156152374985181/user/100000607292435/": "https://www.facebook.com/groups/156152374985181",
        "https://www.facebook.com/groups/corvitarts": "https://www.facebook.com/groups/corvitarts",
    },
    fb.FacebookOldPageUrl: {
        "https://www.facebook.com/pages/category/Artist/Keith-Byrne-Art-243104839060471/": "https://www.facebook.com/pages/category/Artist/Keith-Byrne-Art-243104839060471",
    },
    fb.FacebookPostUrl: {
        "https://www.facebook.com/comaofsoulsart/photos/a.1533192583644740.1073741828.1533190756978256/1564060640557934/?type=3\u0026theater": "https://www.facebook.com/comaofsoulsart/posts/1564060640557934",
        "https://www.facebook.com/annamakkotan/posts/676864725988821/": "https://www.facebook.com/annamakkotan/posts/676864725988821",

        "https://www.facebook.com/TypeMoonWorld/photos/3060422500867494": "https://www.facebook.com/TypeMoonWorld/posts/3060422500867494",
        "https://www.facebook.com/TypeMoonWorld/posts/3060422500867494": "https://www.facebook.com/TypeMoonWorld/posts/3060422500867494",
        "https://www.facebook.com/TypeMoonWorld/photos/pcb.3060422600867484/3060422470867497/?type=3&theater": "https://www.facebook.com/TypeMoonWorld/posts/3060422470867497",
        "https://www.facebook.com/fkscrashing/posts/pfbid02DGobMuY9xXcdnitCwBQxAL6hXBgATLMprXdU4afdoTabjvULYj9LLQRxFmdCcW3Yl": "https://www.facebook.com/fkscrashing/posts/pfbid02DGobMuY9xXcdnitCwBQxAL6hXBgATLMprXdU4afdoTabjvULYj9LLQRxFmdCcW3Yl",
        "https://m.facebook.com/global.honkaiimpact/posts/wallpaper-honkai-quest-wallpaper-selection-click-the-link-using-pc-to-download-t/695401147785427/": "https://www.facebook.com/global.honkaiimpact/posts/695401147785427",
        "https://www.facebook.com/HonkaiImpact3rd/videos/starlit-astrologos/254387989185091/": "https://www.facebook.com/HonkaiImpact3rd/posts/254387989185091",
        "https://www.facebook.com/BoltertoKokoro/photos/a.1329829920487418/1470977829705959/?type=3://scontent.fbwn1-1.fna.fbcdn.net/v/t1.0-9/60859695_1470977833039292_7758017375433129984_n.jpg?_nc_cat=103\u0026_nc_ht=scontent.fbwn1-1.fna\u0026oh=da6331cbe01e7adf90381f7f42a46ef6\u0026oe=5D5268E9": "https://www.facebook.com/BoltertoKokoro/posts/1470977829705959",
    },
    fb.FacebookMediaSetUrl: {
        "https://www.facebook.com/media/set/?set=a.1972049129486802": "https://www.facebook.com/media/set/?set=a.1972049129486802",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
