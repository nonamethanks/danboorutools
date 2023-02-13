from danboorutools.models.url import ArtistUrl, AssetUrl, PostUrl, RedirectUrl
from danboorutools.util.misc import compile_url

_BASE_REGEX = r"https?:\/\/(?:(?:www\.)?fanbox\.cc\/@(?P<artist_id>[\w-]+)|(?P<artist_id>(?!downloads|www)[\w-]+)\.fanbox\.cc)"
REGEX_ARTIST = compile_url(_BASE_REGEX, r"(?:\/?\w+)?$")
REGEX_POST = compile_url(_BASE_REGEX, r"\/posts\/(?P<post_id>\d+)")
REGEX_OLD_POST = compile_url(r"pixiv\.net\/fanbox\/creator\/(?P<pixiv_artist_id>\d+)\/post\/(?P<post_id>\d+)")
REGEX_OLD_ARTIST = compile_url(r"pixiv\.net\/fanbox\/(user\/|creator\/|member\.php\?user_id=)(?P<pixiv_artist_id>\d+)(?:\/(?:\w+)?)?$")


REGEX_IMAGE_1 = r"(?:downloads\.fanbox\.cc|fanbox.pixiv.net|pixiv.pximg.net)\/images\/post\/(?P<post_id>\d+)(?:\/\w+)?"
REGEX_IMAGE_2 = r"pixiv\.pximg\.net\/(?:c\/\w+\/)?fanbox\/public\/images\/(?:post\/(?P<post_id>\d+)|creator\/(?P<pixiv_artist_id>\d+))"
REGEX_IMAGE = compile_url(r"https?:\/\/(?:" + REGEX_IMAGE_1 + "|" + REGEX_IMAGE_2 + r")(?:\/\w+)?\/(?P<image_id>\w+)\.\w+")


class FanboxPostUrl(PostUrl):
    test_cases = [
        "https://www.fanbox.cc/@tsukiori/posts/1080657",

        "https://omu001.fanbox.cc/posts/39714"
        "https://brllbrll.fanbox.cc/posts/626093",  # R18
    ]
    domains = ["fanbox.cc"]
    pattern = REGEX_POST
    normalization = "https://{artist_id}.fanbox.cc/posts/{post_id}"
    id_name = "post_id"


class FanboxArtistUrl(ArtistUrl):
    test_cases = [
        "https://www.fanbox.cc/@tsukiori",

        "https://omu001.fanbox.cc",
        "https://omu001.fanbox.cc/posts",
        "https://omu001.fanbox.cc/plans",
    ]
    domains = ["fanbox.cc"]
    pattern = REGEX_ARTIST
    normalization = "https://{artist_id}.fanbox.cc"
    id_name = "artist_id"


class FanboxOldPostUrl(RedirectUrl):
    test_cases = [
        "https://pixiv.net/fanbox/creator/1566167/post/39714",
        "https://www.pixiv.net/fanbox/creator/1566167/post/39714",
    ]
    domains = ["pixiv.net"]
    pattern = REGEX_OLD_POST
    normalization = "https://www.pixiv.net/fanbox/creator/{pixiv_artist_id}/post/{post_id}"
    id_name = "post_id"


class FanboxOldArtistUrl(RedirectUrl):
    test_cases = [
        "https://pixiv.net/fanbox/creator/1566167",
        "https://www.pixiv.net/fanbox/creator/1566167",
        "https://www.pixiv.net/fanbox/user/3410642",
        "https://www.pixiv.net/fanbox/creator/18915237/post",

        "http://pixiv.net/fanbox/member.php?user_id=3410642",
        "http://www.pixiv.net/fanbox/member.php?user_id=3410642",
    ]
    domains = ["pixiv.net"]
    pattern = REGEX_OLD_ARTIST
    normalization = "https://www.pixiv.net/fanbox/creator/{pixiv_artist_id}"
    id_name = "pixiv_artist_id"

    # TODO: implement related pixiv -> fanbox and fanbox -> pixiv


class FanboxImageUrl(AssetUrl):
    test_cases = [
        "https://downloads.fanbox.cc/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png",  # full res
        "https://downloads.fanbox.cc/images/post/39714/c/1200x630/JvjJal8v1yLgc5DPyEI05YpT.jpeg",  # sample
        "https://downloads.fanbox.cc/images/post/39714/w/1200/JvjJal8v1yLgc5DPyEI05YpT.jpeg",  # sample
        "https://fanbox.pixiv.net/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png",  # old

        "https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg",
        "https://pixiv.pximg.net/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg",

        "https://pixiv.pximg.net/c/400x400_90_a2_g5/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg",
        "https://pixiv.pximg.net/c/1620x580_90_a2_g5/fanbox/public/images/creator/1566167/cover/QqxYtuWdy4XWQx1ZLIqr4wvA.jpeg",
        "https://pixiv.pximg.net/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg",  # dead
    ]
    id_name = "image_id"
    pattern = REGEX_IMAGE
    domains = ["fanbox.cc", "pixiv.net", "pximg.net"]
    # https://null.fanbox.cc/39714 TODO: use this to get the post
