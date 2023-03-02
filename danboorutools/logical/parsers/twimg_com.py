from danboorutools.exceptions import UnparsableUrl
from danboorutools.logical.extractors.twitter import TwitterArtistImageUrl, TwitterAssetUrl, TwitterUrl
from danboorutools.logical.parsers import ParsableUrl, UrlParser


class TwimgComParser(UrlParser):
    test_cases = {
        TwitterAssetUrl: [
            "https://video.twimg.com/tweet_video/E_8lAMJUYAIyenr.mp4",
            "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/pl/Srzcr2EsBK5Mwlvf.m3u8?tag=12&container=fmp4",
            "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/360x270/SygSrUcDpCr1AnOf.mp4?tag=12",
            "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/960x720/wiC1XIw8QehhL5JL.mp4?tag=12",
            "https://video.twimg.com/ext_tw_video/1496554514312269828/pu/vid/480x360/amWjOw0MmLdnPMPB.mp4?tag=12",
            "https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb.jpg",
            "https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb.jpg:small",
            "https://pbs.twimg.com/media/EBGbJe_U8AA4Ekb?format=jpg&name=900x900",
            "https://pbs.twimg.com/tweet_video_thumb/ETkN_L3X0AMy1aT.jpg",
            "https://pbs.twimg.com/ext_tw_video_thumb/1243725361986375680/pu/img/JDA7g7lcw7wK-PIv.jpg",
            "https://pbs.twimg.com/amplify_video_thumb/1215590775364259840/img/lolCkEEioFZTb5dl.jpg",
            "https://p.twimg.com/Ax7-w7ZCMAAQegx.jpg:large",
        ],
        TwitterArtistImageUrl: [
            "https://pbs.twimg.com/profile_banners/780804311529906176/1475001696",
            "https://pbs.twimg.com/profile_banners/780804311529906176/1475001696/600x200",
            "https://si0.twimg.com/profile_background_images/816078776/5691fe91c3ad0f6627cd00fa22d1f610.jpeg",
            "http://a1.twimg.com/profile_background_images/108010950/CosmicBreak09_summer.JPG",
        ],
    }

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> TwitterUrl | None:
        instance: TwitterUrl
        match parsable_url.url_parts:
            case "media", filename:
                instance = TwitterAssetUrl(parsable_url)
                instance.file_path = "/".join(parsable_url.url_parts).split(":")[0]
                if "." not in filename:
                    instance.file_path = instance.file_path + "." + parsable_url.query["format"]
            case ("tweet_video" | "ext_tw_video" | "ext_tw_video_thumb" | "tweet_video_thumb" | "amplify_video_thumb"), *_subdirs, _filename:
                instance = TwitterAssetUrl(parsable_url)
                instance.file_path = "/".join(parsable_url.url_parts)
            case "profile_banners", user_id, file_id, *_:
                instance = TwitterArtistImageUrl(parsable_url)
                instance.user_id = int(user_id)
                instance.file_path = f"profile_banners/{user_id}/{file_id}/1500x500"
            case "profile_background_images", user_id, _:
                instance = TwitterArtistImageUrl(parsable_url)
                instance.user_id = int(user_id)
                instance.file_path = "/".join(parsable_url.url_parts)
            case filename, if parsable_url.subdomain == "p":
                instance = TwitterAssetUrl(parsable_url)
                instance.file_path = "/".join(parsable_url.url_parts).rpartition(":")[0]
                if "." not in filename:
                    instance.file_path = instance.file_path + "." + parsable_url.query["format"]

            # "https://pbs.twimg.com/card_img/831677993668005888/m1NfMR3R?format=jpg\u0026name=orig",
            case "card_img", _, _:
                raise UnparsableUrl(parsable_url)

            # https://o.twimg.com/1/proxy.jpg?t=FQQVBBgpaHR0cHM6Ly90d2l0cGljLmNvbS9zaG93L2xhcmdlL2MxNTU4bi5qcGcUBBYAEgA\u0026s=Ssrtv1f9v1MbLoHIO8b1p_b2lArUwWom4xLBzhDgCQc
            # https://o.twimg.com/2/proxy.jpg?t=HBgpaHR0cHM6Ly90d2l0cGljLmNvbS9zaG93L2xhcmdlL2NoYWphMy5qcGcUsAkUwAwAFgASAA\u0026s=cngq8FnWbQcMihBgX2-BwIozkcKILHzjn5Y3Vmt7LS8
            case _, "proxy.jpg":
                raise UnparsableUrl(parsable_url)

            # "http://a0.twimg.com/profile_images/1643478211/1426283i.jpg",
            case "profile_images", _, _:
                raise UnparsableUrl(parsable_url)

            case _:
                return None

        return instance
