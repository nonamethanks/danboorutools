from ward import test

from danboorutools.models.url import Url

urls = {
    "https://www.weibo.com/u/5501756072": "https://www.weibo.com/u/5501756072",
    "https://www.weibo.com/u/5957640693/home?wvr=5": "https://www.weibo.com/u/5957640693",
    "https://m.weibo.cn/profile/5501756072": "https://www.weibo.com/u/5501756072",
    "https://m.weibo.cn/u/5501756072": "https://www.weibo.com/u/5501756072",
    "https://www.weibo.com/p/1005055399876326": "https://www.weibo.com/p/1005055399876326",
    "https://www.weibo.com/p/1005055399876326/home?from=page_100505&mod=TAB&is_hot=1": "https://www.weibo.com/p/1005055399876326",
    "https://www.weibo.cn/p/1005055399876326": "https://www.weibo.com/p/1005055399876326",
    "https://m.weibo.com/p/1005055399876326": "https://www.weibo.com/p/1005055399876326",
    "https://www.weibo.com/5501756072": "https://www.weibo.com/u/5501756072",
    "https://www.weibo.cn/5501756072": "https://www.weibo.com/u/5501756072",
    "https://weibo.com/1843267214/profile": "https://www.weibo.com/u/1843267214",
    "https://weibo.com/n/肆巳4": "https://www.weibo.com/n/肆巳4",
    "https://www.weibo.com/n/小小男爵不要坑": "https://www.weibo.com/n/小小男爵不要坑",
    "https://www.weibo.com/endlessnsmt": "https://www.weibo.com/endlessnsmt",
    "https://www.weibo.cn/endlessnsmt": "https://www.weibo.com/endlessnsmt",
    "https://www.weibo.com/lvxiuzi0/home": "https://www.weibo.com/lvxiuzi0",

    "http://tw.weibo.com/1300957955/3786333853668537": "https://www.weibo.com/1300957955/3786333853668537",
    "http://weibo.com/3357910224/EEHA1AyJP": "https://www.weibo.com/3357910224/EEHA1AyJP",
    "https://www.weibo.com/5501756072/IF9fugHzj?from=page_1005055501756072_profile&wvr=6&mod=weibotime": "https://www.weibo.com/5501756072/IF9fugHzj",
    "http://photo.weibo.com/2125874520/wbphotos/large/mid/4194742441135220/pid/7eb64558gy1fnbryb5nzoj20dw10419t": "https://www.weibo.com/detail/4194742441135220",
    "http://photo.weibo.com/5732523783/talbum/detail/photo_id/4029784374069389?prel=p6_3": "https://www.weibo.com/detail/4029784374069389",
    "https://m.weibo.cn/detail/4506950043618873": "https://www.weibo.com/detail/4506950043618873",
    "https://www.weibo.com/detail/4676597657371957": "https://www.weibo.com/detail/4676597657371957",

    "https://share.api.weibo.cn/share/304950356,4767694689143828.html": "https://www.weibo.com/detail/304950356",
    "https://share.api.weibo.cn/share/304950356,4767694689143828": "https://www.weibo.com/detail/304950356",
    "https://m.weibo.cn/status/J33G4tH1B": "https://m.weibo.cn/status/J33G4tH1B",

    "http://ww1.sinaimg.cn/large/69917555gw1f6ggdghk28j20c87lbhdt.jpg": "https://ww1.sinaimg.cn/large/69917555gw1f6ggdghk28j20c87lbhdt.jpg",
    "https://wx1.sinaimg.cn/large/002NQ2vhly1gqzqfk1agfj62981aw4qr02.jpg": "https://wx1.sinaimg.cn/large/002NQ2vhly1gqzqfk1agfj62981aw4qr02.jpg",
    "http://ww4.sinaimg.cn/mw690/77a2d531gw1f4u411ws3aj20m816fagg.jpg": "https://ww4.sinaimg.cn/large/77a2d531gw1f4u411ws3aj20m816fagg.jpg",
    "https://wx4.sinaimg.cn/orj360/e3930166gy1g546bz86cij20u00u040y.jpg": "https://wx4.sinaimg.cn/large/e3930166gy1g546bz86cij20u00u040y.jpg",
    "http://ww3.sinaimg.cn/mw1024/0065kjmOgw1fabcanrzx6j30f00lcjwv.jpg": "https://ww3.sinaimg.cn/large/0065kjmOgw1fabcanrzx6j30f00lcjwv.jpg",
    "https://wx1.sinaimg.cn/original/7004ec1cly1ge9dcbsw4lj20jg2ir7wh.jpg": "https://wx1.sinaimg.cn/large/7004ec1cly1ge9dcbsw4lj20jg2ir7wh.jpg",
    # "http://s2.sinaimg.cn/middle/645f3c7fg7715a2e3b711\u0026690": "http://s2.sinaimg.cn/middle/645f3c7fg7715a2e3b711\u0026690",
    # "http://s3.sinaimg.cn/orignal/7011f2d7hec2cafbb7dc2\u0026amp;690": "http://s3.sinaimg.cn/orignal/7011f2d7hec2cafbb7dc2\u0026amp;690",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
