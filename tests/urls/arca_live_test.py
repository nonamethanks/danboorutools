import pytest

from danboorutools.logical.urls.arca_live import ArcaLiveArtistUrl, ArcaLiveImageUrl, ArcaLivePostUrl
from tests.helpers.parsing import generate_parsing_test

urls = {
    ArcaLivePostUrl: {
        "https://arca.live/b/arknights/66031722": "https://arca.live/b/arknights/66031722",
    },
    ArcaLiveArtistUrl: {
        "https://arca.live/u/@Si리링": "https://arca.live/u/@Si리링",
        "https://arca.live/u/@Nauju/45320365": "https://arca.live/u/@Nauju/45320365",
    },
    ArcaLiveImageUrl: {
        "https://ac2.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg": "https://ac2.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg?type=orig",
        "https://ac2.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg?type=orig": "https://ac2.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg?type=orig",
        "https://ac2-o.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg?type=orig": "https://ac2-o.namu.la/20221225sac2/e06dcf8edd29c597240898a6752c74dbdd0680fc932cfd0ecc898795f1db34b5.jpg?type=orig",
        "https://ac.namu.la/20221211sac/5ea7fbca5e49ec16beb099fc6fc991690d37552e599b1de8462533908346241e.png": "https://ac.namu.la/20221211sac/5ea7fbca5e49ec16beb099fc6fc991690d37552e599b1de8462533908346241e.png?type=orig",
        "https://ac-o.namu.la/20221211sac/7f73beefc4f18a2f986bc4c6821caba706e27f4c94cb828fc16e2af1253402d9.gif?type=orig": "https://ac-o.namu.la/20221211sac/7f73beefc4f18a2f986bc4c6821caba706e27f4c94cb828fc16e2af1253402d9.gif?type=orig",
        "https://ac.namu.la/20221211sac/7f73beefc4f18a2f986bc4c6821caba706e27f4c94cb828fc16e2af1253402d9.mp4": "https://ac.namu.la/20221211sac/7f73beefc4f18a2f986bc4c6821caba706e27f4c94cb828fc16e2af1253402d9.gif?type=orig",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
