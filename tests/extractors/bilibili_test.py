# pylint: disable=cell-var-from-loop
from ward import test

from danboorutools.models.url import Url

urls = {
    "https://t.bilibili.com/686082748803186697": "https://t.bilibili.com/686082748803186697",
    "https://t.bilibili.com/723052706467414039?spm_id_from=333.999.0.0": "https://t.bilibili.com/723052706467414039",
    "https://t.bilibili.com/h5/dynamic/detail/410234698927673781": "https://t.bilibili.com/410234698927673781",

    "https://m.bilibili.com/dynamic/612214375070704555": "https://t.bilibili.com/612214375070704555",
    "https://www.bilibili.com/opus/684571925561737250": "https://t.bilibili.com/684571925561737250",
    "https://h.bilibili.com/83341894": "https://h.bilibili.com/83341894",

    "https://www.bilibili.com/p/h5/8773541": "https://h.bilibili.com/8773541",

    "https://www.bilibili.com/read/cv7360489": "https://www.bilibili.com/read/cv7360489",

    "https://www.bilibili.com/video/BV1dY4y1u7Vi/": "https://www.bilibili.com/video/BV1dY4y1u7Vi",
    "http://www.bilibili.tv/video/av439451/": "https://www.bilibili.com/video/av439451",

    "https://space.bilibili.com/355143": "https://space.bilibili.com/355143",
    "https://space.bilibili.com/476725595/dynamic": "https://space.bilibili.com/476725595",
    "https://space.bilibili.com/476725595/video": "https://space.bilibili.com/476725595",
    "http://www.bilibili.tv/member/index.php?mid=66804": "https://space.bilibili.com/66804",
    "https://h.bilibili.com/member?mod=space%5Cu0026uid=4617101%5Cu0026act=p_index": "https://space.bilibili.com/4617101",
    "https://link.bilibili.com/p/world/index#/32122361/world/": "https://space.bilibili.com/32122361",
    "https://m.bilibili.com/space/489905": "https://space.bilibili.com/489905",
    "http://space.bilibili.com/13574506#/album": "https://space.bilibili.com/13574506",

    "https://live.bilibili.com/43602": "https://live.bilibili.com/43602",


}

for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
