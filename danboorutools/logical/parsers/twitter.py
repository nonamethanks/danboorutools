from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.extractors import twitter as tw
from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.models.url import UselessUrl


class TwitterComParser(UrlParser):
    RESERVED_NAMES = ["home", "i", "intent", "search", "hashtag", "about", "twitter"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> tw.TwitterUrl | UselessUrl | None:
        if parsable_url.subdomain not in ["www", ""]:
            return UselessUrl(parsable_url)

        instance: tw.TwitterUrl
        match parsable_url.url_parts:
            # https://twitter.com/i/web/status/943446161586733056
            # https://twitter.com/i/status/943446161586733056
            case "i", *_, "status", post_id:
                instance = tw.TwitterOnlyStatusUrl(parsable_url)
                instance.post_id = int(post_id.removesuffix("#m"))

            # https://twitter.com/motty08111213/status/943446161586733056
            # https://twitter.com/motty08111213/status/943446161586733056?s=19
            # https://twitter.com/Kekeflipnote/status/1496555599718498319/video/1
            # https://twitter.com/sato_1_11/status/1496489742791475201/photo/2
            case username, "status", post_id, *_:
                instance = tw.TwitterPostUrl(parsable_url)
                instance.username = username
                instance.post_id = int(post_id.removesuffix("#m"))

            # https://pic.twitter.com/Dxn7CuVErW
            case shortener_id, if parsable_url.subdomain == "pic":
                instance = tw.TwitterShortenerUrl(parsable_url)
                instance.shortener_id = shortener_id

            # https://twitter.com/motty08111213
            # https://twitter.com/motty08111213/likes
            case username, *_ if username.lower() not in cls.RESERVED_NAMES:
                instance = tw.TwitterArtistUrl(parsable_url)
                instance.username = username

            # https://twitter.com/i/user/889592953
            case "i", "user", user_id:
                instance = tw.TwitterIntentUrl(parsable_url)
                instance.intent_id = int(user_id)

            # https://twitter.com/intent/user?user_id=2819289818
            case "intent", "user" if "user_id" in parsable_url.query:
                instance = tw.TwitterIntentUrl(parsable_url)
                instance.intent_id = int(parsable_url.query["user_id"])

            # https://twitter.com/intent/user?screen_name=ryuudog_NFT
            case "intent", "user" if "screen_name" in parsable_url.query:
                instance = tw.TwitterArtistUrl(parsable_url)
                instance.username = parsable_url.query["screen_name"]

            # https://twitter.com/intent/favorite?tweet_id=1300476511254753280
            case "intent", "favorite":
                instance = tw.TwitterOnlyStatusUrl(parsable_url)
                instance.post_id = int(parsable_url.query["tweet_id"])

            case subdir, *_ if subdir.lower() in cls.RESERVED_NAMES:
                return UselessUrl(parsable_url)

            case "i", "timeline":
                return UselessUrl(parsable_url)

            case _:
                return None

        return instance


class TwimgComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> tw.TwitterUrl | None:
        instance: tw.TwitterUrl
        match parsable_url.url_parts:
            # https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb.jpg
            # https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb.jpg:small
            # https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb?format=jpg&name=900x900
            case "media", filename:
                instance = tw.TwitterAssetUrl(parsable_url)
                instance.file_path = "/".join(parsable_url.url_parts).partition(":")[0]
                if "." not in filename:
                    instance.file_path = instance.file_path + "." + parsable_url.query["format"]

            # https://video.twimg.com/tweet_video/E_8lAMJUYAIyenr.mp4
            # https://video.twimg.com/ext_tw_video/1496554514312269828/pu/pl/Srzcr2EsBK5Mwlvf.m3u8?tag=12&container=fmp4
            # https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/360x270/SygSrUcDpCr1AnOf.mp4?tag=12
            # https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/960x720/wiC1XIw8QehhL5JL.mp4?tag=12
            # https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/480x360/amWjOw0MmLdnPMPB.mp4?tag=12
            # https://pbs.twimg.com/tweet_video_thumb/ETkN_L3X0AMy1aT.jpg
            # https://pbs.twimg.com/ext_tw_video_thumb/1243725361986375680/pu/img/JDA7g7lcw7wK-PIv.jpg
            # https://pbs.twimg.com/amplify_video_thumb/1215590775364259840/img/lolCkEEioFZTb5dl.jpg
            case ("tweet_video" | "ext_tw_video" | "ext_tw_video_thumb" | "tweet_video_thumb" | "amplify_video_thumb"), *_dirs, _filename:
                instance = tw.TwitterAssetUrl(parsable_url)
                instance.file_path = "/".join(parsable_url.url_parts)

            # https://pbs.twimg.com/profile_banners/780804311529906176/1475001696
            # https://pbs.twimg.com/profile_banners/780804311529906176/1475001696/600x200
            case "profile_banners", user_id, file_id, *_:
                instance = tw.TwitterArtistImageUrl(parsable_url)
                instance.user_id = int(user_id)
                instance.file_path = f"profile_banners/{user_id}/{file_id}/1500x500"

            # https://si0.twimg.com/profile_background_images/816078776/5691fe91c3ad0f6627cd00fa22d1f610.jpeg
            # http://a1.twimg.com/profile_background_images/108010950/CosmicBreak09_summer.JPG
            case "profile_background_images", user_id, _:
                instance = tw.TwitterArtistImageUrl(parsable_url)
                instance.user_id = int(user_id)
                instance.file_path = "/".join(parsable_url.url_parts)

            # https://p.twimg.com/Ax7-w7ZCMAAQegx.jpg:large
            case filename, if parsable_url.subdomain == "p":
                instance = tw.TwitterAssetUrl(parsable_url)
                instance.file_path = "/".join(parsable_url.url_parts).rpartition(":")[0]
                if "." not in filename:
                    instance.file_path = instance.file_path + "." + parsable_url.query["format"]

            # https://pbs.twimg.com/card_img/831677993668005888/m1NfMR3R?format=jpg\u0026name=orig
            case "card_img", _, _:
                raise UnparsableUrlError(parsable_url)

            # https://o.twimg.com/1/proxy.jpg?t=FQQVBBgpaHR0cHM6Ly90d2l0cGljLmNvbS9zaG93L2xhcmdlL2MxNTU4bi5qcGcUBBYAEgA\u0026s=Ssrtv1f9v1MbLoHIO8b1p_b2lArUwWom4xLBzhDgCQc
            # https://o.twimg.com/2/proxy.jpg?t=HBgpaHR0cHM6Ly90d2l0cGljLmNvbS9zaG93L2xhcmdlL2NoYWphMy5qcGcUsAkUwAwAFgASAA\u0026s=cngq8FnWbQcMihBgX2-BwIozkcKILHzjn5Y3Vmt7LS8
            case _, "proxy.jpg":
                raise UnparsableUrlError(parsable_url)

            # http://a0.twimg.com/profile_images/1643478211/1426283i.jpg
            case "profile_images", _, _:
                raise UnparsableUrlError(parsable_url)

            case _:
                return None

        return instance


class TCoParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> tw.TwitterShortenerUrl | None:
        match parsable_url.url_parts:
            # https://t.co/Dxn7CuVErW
            case shortener_id, :
                instance = tw.TwitterShortenerUrl(parsable_url)
                instance.shortener_id = shortener_id
            case _:
                return None

        return instance
