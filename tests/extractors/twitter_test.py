from ward import test

from danboorutools.models.url import Url

urls = {
    "https://t.co/Dxn7CuVErW": "https://t.co/Dxn7CuVErW",


    "https://twitter.com/intent/user?screen_name=ryuudog_NFT": "https://twitter.com/ryuudog_NFT",
    "https://twitter.com/motty08111213": "https://twitter.com/motty08111213",
    "https://twitter.com/motty08111213/likes": "https://twitter.com/motty08111213",

    "https://twitter.com/motty08111213/status/943446161586733056": "https://twitter.com/motty08111213/status/943446161586733056",
    "https://twitter.com/motty08111213/status/943446161586733056?s=19": "https://twitter.com/motty08111213/status/943446161586733056",
    "https://twitter.com/Kekeflipnote/status/1496555599718498319/video/1": "https://twitter.com/Kekeflipnote/status/1496555599718498319",
    "https://twitter.com/sato_1_11/status/1496489742791475201/photo/2": "https://twitter.com/sato_1_11/status/1496489742791475201",
    "https://twitter.com/i/web/status/943446161586733056": "https://twitter.com/i/status/943446161586733056",
    "https://twitter.com/i/status/943446161586733056": "https://twitter.com/i/status/943446161586733056",
    "https://twitter.com/intent/favorite?tweet_id=1300476511254753280": "https://twitter.com/i/status/1300476511254753280",

    "https://twitter.com/i/user/889592953": "https://twitter.com/intent/user?user_id=889592953",
    "https://twitter.com/intent/user?user_id=2819289818": "https://twitter.com/intent/user?user_id=2819289818",

    "https://pic.twitter.com/Dxn7CuVErW": "https://t.co/Dxn7CuVErW",

    # "https://video.twimg.com/tweet_video/E_8lAMJUYAIyenr.mp4": "https://video.twimg.com/tweet_video/E_8lAMJUYAIyenr.mp4",
    # "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/pl/Srzcr2EsBK5Mwlvf.m3u8?tag=12&container=fmp4": "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/pl/Srzcr2EsBK5Mwlvf.m3u8?tag=12&container=fmp4",
    # "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/360x270/SygSrUcDpCr1AnOf.mp4?tag=12": "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/360x270/SygSrUcDpCr1AnOf.mp4?tag=12",
    # "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/960x720/wiC1XIw8QehhL5JL.mp4?tag=12": "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/960x720/wiC1XIw8QehhL5JL.mp4?tag=12",
    # "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/480x360/amWjOw0MmLdnPMPB.mp4?tag=12": "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/480x360/amWjOw0MmLdnPMPB.mp4?tag=12",
    "https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb.jpg": "https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb.jpg:orig",
    "https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb.jpg:small": "https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb.jpg:orig",
    "https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb?format=jpg&name=900x900": "https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb.jpg:orig",
    "https://pbs.twimg.com/tweet_video_thumb/ETkN_L3X0AMy1aT.jpg": "https://pbs.twimg.com/tweet_video_thumb/ETkN_L3X0AMy1aT.jpg:orig",
    "https://pbs.twimg.com/ext_tw_video_thumb/1243725361986375680/pu/img/JDA7g7lcw7wK-PIv.jpg": "https://pbs.twimg.com/ext_tw_video_thumb/1243725361986375680/pu/img/JDA7g7lcw7wK-PIv.jpg:orig",
    "https://pbs.twimg.com/amplify_video_thumb/1215590775364259840/img/lolCkEEioFZTb5dl.jpg": "https://pbs.twimg.com/amplify_video_thumb/1215590775364259840/img/lolCkEEioFZTb5dl.jpg:orig",
    "https://p.twimg.com/Ax7-w7ZCMAAQegx.jpg:large": "https://p.twimg.com/Ax7-w7ZCMAAQegx.jpg:orig",

    "https://pbs.twimg.com/profile_banners/780804311529906176/1475001696": "https://pbs.twimg.com/profile_banners/780804311529906176/1475001696/1500x500",
    "https://pbs.twimg.com/profile_banners/780804311529906176/1475001696/600x200": "https://pbs.twimg.com/profile_banners/780804311529906176/1475001696/1500x500",
    "https://si0.twimg.com/profile_background_images/816078776/5691fe91c3ad0f6627cd00fa22d1f610.jpeg": "https://si0.twimg.com/profile_background_images/816078776/5691fe91c3ad0f6627cd00fa22d1f610.jpeg",
    "http://a1.twimg.com/profile_background_images/108010950/CosmicBreak09_summer.JPG": "https://a1.twimg.com/profile_background_images/108010950/CosmicBreak09_summer.JPG",
}


for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
