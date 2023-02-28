
from ward import test

from danboorutools.models.url import Url

urls = {
    "https://www.nicovideo.jp/watch/sm36465441": "https://www.nicovideo.jp/watch/sm36465441",
    "https://www.nicovideo.jp/watch/nm36465441": "https://www.nicovideo.jp/watch/nm36465441",
    "http://nine.nicovideo.jp/watch/nm13933079": "https://www.nicovideo.jp/watch/nm13933079",
    "http://www.nicovideo.jp/watch/1488526447": "https://www.nicovideo.jp/watch/1488526447",

    "https://www.nicovideo.jp/user/4572975": "https://www.nicovideo.jp/user/4572975",
    "https://www.nicovideo.jp/user/20446930/mylist/28674289": "https://www.nicovideo.jp/user/20446930",
    "https://q.nicovideo.jp/users/18700356": "https://www.nicovideo.jp/user/18700356",
    "http://www.nicovideo.jp/mylist/2858074/4602763": "https://www.nicovideo.jp/user/2858074",

    "https://com.nicovideo.jp/community/co24880": "https://com.nicovideo.jp/community/co24880",

    "http://www.nicovideo.jp/mylist/21474275": "http://www.nicovideo.jp/mylist/21474275",
    "http://www.nicovideo.jp/mylist/37220827#+sort=1": "http://www.nicovideo.jp/mylist/37220827",

    "https://game.nicovideo.jp/atsumaru/users/7757217": "https://game.nicovideo.jp/atsumaru/users/7757217",

    "http://nico.ms/co2744246": "https://com.nicovideo.jp/community/co2744246",

    "http://nico.ms/user/43606505": "https://www.nicovideo.jp/user/43606505",

    "https://nico.ms/nm36465441": "https://www.nicovideo.jp/watch/nm36465441",
    "https://nico.ms/sm36465441": "https://www.nicovideo.jp/watch/sm36465441",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
