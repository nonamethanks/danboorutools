from danboorutools.logical.urls import twitter as tw
from danboorutools.models.url import UselessUrl
from tests.urls import assert_artist_url, assert_info_url, generate_parsing_suite

urls = {
    tw.TwitterShortenerUrl: {
        "https://t.co/Dxn7CuVErW": "https://t.co/Dxn7CuVErW",
        "https://pic.twitter.com/Dxn7CuVErW": "https://t.co/Dxn7CuVErW",
    },
    tw.TwitterAssetUrl: {
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

    },
    tw.TwitterArtistImageUrl: {
        "https://pbs.twimg.com/profile_banners/780804311529906176/1475001696": "https://pbs.twimg.com/profile_banners/780804311529906176/1475001696/1500x500",
        "https://pbs.twimg.com/profile_banners/780804311529906176/1475001696/600x200": "https://pbs.twimg.com/profile_banners/780804311529906176/1475001696/1500x500",
        "https://si0.twimg.com/profile_background_images/816078776/5691fe91c3ad0f6627cd00fa22d1f610.jpeg": "https://si0.twimg.com/profile_background_images/816078776/5691fe91c3ad0f6627cd00fa22d1f610.jpeg",
        "http://a1.twimg.com/profile_background_images/108010950/CosmicBreak09_summer.JPG": "https://a1.twimg.com/profile_background_images/108010950/CosmicBreak09_summer.JPG",
    },
    tw.TwitterIntentUrl: {
        "https://twitter.com/i/user/889592953": "https://twitter.com/intent/user?user_id=889592953",
        "https://twitter.com/intent/user?user_id=2819289818": "https://twitter.com/intent/user?user_id=2819289818",
    },
    tw.TwitterArtistUrl: {
        "https://twitter.com/intent/user?screen_name=ryuudog_NFT": "https://twitter.com/ryuudog_NFT",
        "https://twitter.com/motty08111213": "https://twitter.com/motty08111213",
        "https://twitter.com/motty08111213/likes": "https://twitter.com/motty08111213",

    },
    tw.TwitterPostUrl: {
        "https://twitter.com/motty08111213/status/943446161586733056": "https://twitter.com/motty08111213/status/943446161586733056",
        "https://twitter.com/motty08111213/status/943446161586733056?s=19": "https://twitter.com/motty08111213/status/943446161586733056",
        "https://twitter.com/Kekeflipnote/status/1496555599718498319/video/1": "https://twitter.com/Kekeflipnote/status/1496555599718498319",
        "https://twitter.com/sato_1_11/status/1496489742791475201/photo/2": "https://twitter.com/sato_1_11/status/1496489742791475201",
    },
    tw.TwitterOnlyStatusUrl: {
        "https://twitter.com/i/web/status/943446161586733056": "https://twitter.com/i/status/943446161586733056",
        "https://twitter.com/i/status/943446161586733056": "https://twitter.com/i/status/943446161586733056",
        "https://twitter.com/intent/favorite?tweet_id=1300476511254753280": "https://twitter.com/i/status/1300476511254753280",
    },
    UselessUrl: {
        "https://twitter.com/hashtag/%E3%82%AC%E3%83%81%E3%83%A3%E3%83%89%E3%83%AD%E3%83%83%E3%82%AF?src=hashtag_click&f=live": "https://twitter.com/hashtag/%E3%82%AC%E3%83%81%E3%83%A3%E3%83%89%E3%83%AD%E3%83%83%E3%82%AF?src=hashtag_click&f=live",
    },
}


generate_parsing_suite(urls)

assert_artist_url(
    "https://twitter.com/ninomaeinanis",
    url_type=tw.TwitterArtistUrl,
    url_properties=dict(username="ninomaeinanis"),
    primary_names=["Ninomae Ina’nis🐙holoEN"],
    secondary_names=["ninomaeinanis", "twitter 1283650008835743744"],
    related=[
        "https://twitter.com/i/events/1390449082599018496",
        "https://twitter.com/intent/user?user_id=1283650008835743744",
        "https://www.youtube.com/channel/UCMwGHR0BTZuLsmjY_NT5Pwg",
    ],
)

assert_artist_url(
    "https://twitter.com/soyso_su40",
    url_type=tw.TwitterArtistUrl,
    url_properties=dict(username="soyso_su40"),
    primary_names=["ポジティブネガ太郎"],
    secondary_names=["soyso_su40", "twitter 2945315071"],
    related=[
        "https://skeb.jp/@soyso_su40",
        "https://twitter.com/intent/user?user_id=2945315071",
    ],
)

assert_info_url(
    "https://twitter.com/intent/user?user_id=354759129",
    url_type=tw.TwitterIntentUrl,
    url_properties=dict(intent_id=354759129),
    primary_names=[],
    secondary_names=[f"twitter 354759129"],
    related=[],
    is_deleted=True,
)
