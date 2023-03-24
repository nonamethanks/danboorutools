from ward import test

from danboorutools.models.url import Url

urls = {
    "http://www.tinami.com/creator/profile/1624": "https://www.tinami.com/creator/profile/1624",
    "https://www.tinami.com/search/list?prof_id=1624": "https://www.tinami.com/creator/profile/1624",

    "http://www.tinami.com/profile/1182": "https://www.tinami.com/profile/1182",
    "http://www.tinami.jp/p/1182": "https://www.tinami.com/profile/1182",

    # "https://img.tinami.com/illust/img/287/497c8a9dc60e6.jpg": "https://img.tinami.com/illust/img/287/497c8a9dc60e6.jpg",
    # "https://img.tinami.com/illust2/img/419/5013fde3406b9.jpg": "https://img.tinami.com/illust2/img/419/5013fde3406b9.jpg",
    # "https://img.tinami.com/illust2/L/452/622f7aa336bf3.gif": "https://img.tinami.com/illust2/L/452/622f7aa336bf3.gif",
    # "https://img.tinami.com/comic/naomao/naomao_001_01.jpg": "https://img.tinami.com/comic/naomao/naomao_001_01.jpg",
    # "https://img.tinami.com/comic/naomao/naomao_002_01.jpg": "https://img.tinami.com/comic/naomao/naomao_002_01.jpg",
    # "https://img.tinami.com/comic/naomao/naomao_topillust.gif": "https://img.tinami.com/comic/naomao/naomao_topillust.gif",

    "https://www.tinami.com/view/461459": "https://www.tinami.com/view/461459",
    "https://www.tinami.com/view/tweet/card/461459": "https://www.tinami.com/view/461459",

    "http://www.tinami.com/comic/naomao/2": "https://www.tinami.com/comic/naomao/2",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
