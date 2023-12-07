import pytest

from danboorutools.logical.urls.geocities import GeocitiesBlogUrl, GeocitiesImageUrl, GeocitiesPageUrl
from tests.helpers.parsing import generate_parsing_test

urls = {
    GeocitiesBlogUrl: {
        "http://www.geocities.jp/express_tsubame/": "http://www.geocities.jp/express_tsubame/",
        "http://www.geocities.com/express_tsubame/": "http://www.geocities.com/express_tsubame/",
    },
    GeocitiesPageUrl: {
        "http://www.geocities.jp/milcho1129/game/mg.html": "",
        "http://www.geocities.jp/kasuga399/image_oebi/": "",
        "http://www.geocities.jp/g_akuta/g_mikuruomake1.2": "",
        "http://www.geocities.jp/hatteneki/img/": "",
    },
    GeocitiesImageUrl: {
        "http://sky.geocities.jp/ranguemont_pass/mdk07.swf": "",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
