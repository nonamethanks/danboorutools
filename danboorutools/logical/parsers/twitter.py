from danboorutools.exceptions import UnparsableUrlError
from danboorutools.logical.url_parser import ParsableUrl, UrlParser
from danboorutools.logical.urls import twitter as tw
from danboorutools.models.url import UselessUrl


class TwitterComParser(UrlParser):
    RESERVED_NAMES = ["home", "i", "intent", "search", "hashtag", "about", "twitter"]

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> tw.TwitterUrl | UselessUrl | None:  # type: ignore[return]
        if parsable_url.subdomain not in ["www", "", "pic", "m", "mobile"]:
            return UselessUrl(parsed_url=parsable_url)

        match parsable_url.url_parts:
            # https://twitter.com/i/web/status/943446161586733056
            # https://twitter.com/i/status/943446161586733056
            case "i", *_, "status", post_id:
                return tw.TwitterOnlyStatusUrl(parsed_url=parsable_url,
                                               post_id=int(post_id.removesuffix("#m")))

            # https://twitter.com/motty08111213/status/943446161586733056
            # https://twitter.com/motty08111213/status/943446161586733056?s=19
            # https://twitter.com/Kekeflipnote/status/1496555599718498319/video/1
            # https://twitter.com/sato_1_11/status/1496489742791475201/photo/2
            case username, "status", post_id, *_:
                return tw.TwitterPostUrl(parsed_url=parsable_url,
                                         username=username,
                                         post_id=int(post_id.removesuffix("#m")))

            # https://pic.twitter.com/Dxn7CuVErW
            case shortener_id, if parsable_url.subdomain == "pic":
                return tw.TwitterShortenerUrl(parsed_url=parsable_url,
                                              shortener_id=shortener_id)

            # https://twitter.com/motty08111213
            # https://twitter.com/motty08111213/likes
            case username, *_ if username.lower() not in cls.RESERVED_NAMES:
                return tw.TwitterArtistUrl(parsed_url=parsable_url,
                                           username=username)

            # https://twitter.com/i/user/889592953
            case "i", "user", user_id:
                return tw.TwitterIntentUrl(parsed_url=parsable_url,
                                           intent_id=int(user_id))

            # https://twitter.com/intent/user?user_id=2819289818
            case "intent", "user" if "user_id" in parsable_url.query:
                return tw.TwitterIntentUrl(parsed_url=parsable_url,
                                           intent_id=int(parsable_url.query["user_id"]))

            # https://twitter.com/intent/user?screen_name=ryuudog_NFT
            case "intent", "user" if "screen_name" in parsable_url.query:
                return tw.TwitterArtistUrl(parsed_url=parsable_url,
                                           username=parsable_url.query["screen_name"])

            # https://twitter.com/intent/favorite?tweet_id=1300476511254753280
            case "intent", "favorite":
                return tw.TwitterOnlyStatusUrl(parsed_url=parsable_url,
                                               post_id=int(parsable_url.query["tweet_id"]))

            case subdir, *_ if subdir.lower() in cls.RESERVED_NAMES:
                return UselessUrl(parsed_url=parsable_url)

            case "i", "timeline":
                return UselessUrl(parsed_url=parsable_url)

            case _:
                return None


class TwimgComParser(UrlParser):
    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> tw.TwitterUrl | None:  # type: ignore[return]
        match parsable_url.url_parts:
            # https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb.jpg
            # https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb.jpg:small
            # https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb?format=jpg&name=900x900
            case "media", filename:
                filename = filename.split(":")[0]
                if "." not in filename:
                    filename = filename + "." + parsable_url.query["format"]
                return tw.TwitterAssetUrl(parsed_url=parsable_url,
                                          file_path=f"media/{filename}")

            # https://p.twimg.com/Ax7-w7ZCMAAQegx.jpg:large
            case filename, if parsable_url.subdomain == "p":
                filename = filename.split(":")[0]
                if "." not in filename:
                    filename = filename + "." + parsable_url.query["format"]
                return tw.TwitterAssetUrl(parsed_url=parsable_url,
                                          file_path=filename)

            # https://video.twimg.com/tweet_video/E_8lAMJUYAIyenr.mp4
            # https://video.twimg.com/ext_tw_video/1496554514312269828/pu/pl/Srzcr2EsBK5Mwlvf.m3u8?tag=12&container=fmp4
            # https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/360x270/SygSrUcDpCr1AnOf.mp4?tag=12
            # https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/960x720/wiC1XIw8QehhL5JL.mp4?tag=12
            # https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/480x360/amWjOw0MmLdnPMPB.mp4?tag=12
            # https://video.twimg.com/amplify_video/1640962950688284675/vid/1920x1080/mqVgMLEUs3VmXIvf.mp4?tag=16
            # https://pbs.twimg.com/tweet_video_thumb/ETkN_L3X0AMy1aT.jpg
            # https://pbs.twimg.com/ext_tw_video_thumb/1243725361986375680/pu/img/JDA7g7lcw7wK-PIv.jpg
            # https://pbs.twimg.com/amplify_video_thumb/1215590775364259840/img/lolCkEEioFZTb5dl.jpg
            case ("tweet_video" | "ext_tw_video" | "ext_tw_video_thumb" | "tweet_video_thumb" | "amplify_video" | "amplify_video_thumb"), *_dirs, _filename:
                return tw.TwitterAssetUrl(parsed_url=parsable_url,
                                          file_path="/".join(parsable_url.url_parts))

            # https://pbs.twimg.com/profile_banners/780804311529906176/1475001696
            # https://pbs.twimg.com/profile_banners/780804311529906176/1475001696/600x200
            case "profile_banners", user_id, file_id, *_:
                return tw.TwitterArtistImageUrl(parsed_url=parsable_url,
                                                user_id=int(user_id),
                                                file_path=f"profile_banners/{user_id}/{file_id}/1500x500")

            # https://si0.twimg.com/profile_background_images/816078776/5691fe91c3ad0f6627cd00fa22d1f610.jpeg
            # http://a1.twimg.com/profile_background_images/108010950/CosmicBreak09_summer.JPG
            case "profile_background_images", user_id, _:
                return tw.TwitterArtistImageUrl(parsed_url=parsable_url,
                                                user_id=int(user_id),
                                                file_path="/".join(parsable_url.url_parts))

            # http://a0.twimg.com/profile_images/1643478211/1426283i.jpg
            # https://pbs.twimg.com/profile_images/1650539849332686849/EzXpyVzB.jpg
            case "profile_images", _, _:
                return tw.TwitterArtistImageUrl(parsed_url=parsable_url,
                                                file_path="/".join(parsable_url.url_parts))

            # https://pbs.twimg.com/card_img/831677993668005888/m1NfMR3R?format=jpg\u0026name=orig
            case "card_img", _, _:
                raise UnparsableUrlError(parsable_url)

            # https://o.twimg.com/1/proxy.jpg?t=FQQVBBgpaHR0cHM6Ly90d2l0cGljLmNvbS9zaG93L2xhcmdlL2MxNTU4bi5qcGcUBBYAEgA\u0026s=Ssrtv1f9v1MbLoHIO8b1p_b2lArUwWom4xLBzhDgCQc
            # https://o.twimg.com/2/proxy.jpg?t=HBgpaHR0cHM6Ly90d2l0cGljLmNvbS9zaG93L2xhcmdlL2NoYWphMy5qcGcUsAkUwAwAFgASAA\u0026s=cngq8FnWbQcMihBgX2-BwIozkcKILHzjn5Y3Vmt7LS8
            case _, "proxy.jpg":
                raise UnparsableUrlError(parsable_url)

            case _:
                return None


class TCoParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> tw.TwitterShortenerUrl | None:
        match parsable_url.url_parts:
            # https://t.co/Dxn7CuVErW
            case shortener_id, :
                return tw.TwitterShortenerUrl(parsed_url=parsable_url,
                                              shortener_id=shortener_id)

            case _:
                return None
