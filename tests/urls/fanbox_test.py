import pytest

from danboorutools.logical.urls import fanbox as f
from tests.helpers.parsing import generate_parsing_test

urls = {
    f.FanboxArtistUrl: {
        "https://www.fanbox.cc/@tsukiori": "https://tsukiori.fanbox.cc",

        "https://omu001.fanbox.cc": "https://omu001.fanbox.cc",
        "https://omu001.fanbox.cc/posts": "https://omu001.fanbox.cc",
        "https://omu001.fanbox.cc/plans": "https://omu001.fanbox.cc",

    },
    f.FanboxAssetUrl: {
        "https://downloads.fanbox.cc/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png": "https://downloads.fanbox.cc/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png",
        "https://downloads.fanbox.cc/images/post/39714/c/1200x630/JvjJal8v1yLgc5DPyEI05YpT.jpeg": "https://downloads.fanbox.cc/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.jpeg",
        "https://downloads.fanbox.cc/images/post/39714/w/1200/JvjJal8v1yLgc5DPyEI05YpT.jpeg": "https://downloads.fanbox.cc/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.jpeg",

        "https://downloads.fanbox.cc/files/post/4978617/T4xNyKH6GB4lJoBbRX2PqzqH.psd": "https://downloads.fanbox.cc/files/post/4978617/T4xNyKH6GB4lJoBbRX2PqzqH.psd",
        "https://downloads.fanbox.cc/files/post/4978617/r3QhOHFnivsSpMtO9KcLhczP.zip": "https://downloads.fanbox.cc/files/post/4978617/r3QhOHFnivsSpMtO9KcLhczP.zip",

        "https://fanbox.pixiv.net/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png": "https://fanbox.pixiv.net/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png",
        "https://fanbox.pixiv.net/files/post/207010/y1qrUK90dn63JXqUE21itupM.png": "https://fanbox.pixiv.net/files/post/207010/y1qrUK90dn63JXqUE21itupM.png",
        "https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg": "https://pixiv.pximg.net/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg",
        "https://pixiv.pximg.net/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg": "https://pixiv.pximg.net/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg",
    },
    f.FanboxPostUrl: {
        "https://www.fanbox.cc/@tsukiori/posts/1080657": "https://tsukiori.fanbox.cc/posts/1080657",

        "https://omu001.fanbox.cc/posts/39714": "https://omu001.fanbox.cc/posts/39714",
        "https://brllbrll.fanbox.cc/posts/626093": "https://brllbrll.fanbox.cc/posts/626093",
    },
    f.FanboxOldPostUrl: {
        "https://pixiv.net/fanbox/creator/1566167/post/39714": "https://www.pixiv.net/fanbox/creator/1566167/post/39714",
        "https://www.pixiv.net/fanbox/creator/1566167/post/39714": "https://www.pixiv.net/fanbox/creator/1566167/post/39714",
    },
    f.FanboxOldArtistUrl: {
        "https://pixiv.net/fanbox/creator/1566167": "https://www.pixiv.net/fanbox/creator/1566167",
        "https://www.pixiv.net/fanbox/creator/1566167": "https://www.pixiv.net/fanbox/creator/1566167",
        "https://www.pixiv.net/fanbox/user/3410642": "https://www.pixiv.net/fanbox/creator/3410642",
        "https://www.pixiv.net/fanbox/creator/18915237/post": "https://www.pixiv.net/fanbox/creator/18915237",
        "http://pixiv.net/fanbox/member.php?user_id=3410642": "https://www.pixiv.net/fanbox/creator/3410642",
        "http://www.pixiv.net/fanbox/member.php?user_id=3410642": "https://www.pixiv.net/fanbox/creator/3410642",

    },
    f.FanboxArtistImageUrl: {
        "https://pixiv.pximg.net/c/400x400_90_a2_g5/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg": "https://pixiv.pximg.net/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg",
        "https://pixiv.pximg.net/c/1620x580_90_a2_g5/fanbox/public/images/creator/1566167/cover/QqxYtuWdy4XWQx1ZLIqr4wvA.jpeg": "https://pixiv.pximg.net/fanbox/public/images/creator/1566167/cover/QqxYtuWdy4XWQx1ZLIqr4wvA.jpeg",
        "https://pixiv.pximg.net/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg": "https://pixiv.pximg.net/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg",
        "https://pixiv.pximg.net/c/160x160_90_a2_g5/fanbox/public/images/user/10013868/icon/HQBS5TrKZRZ0gEZrsbmtCX3b.jpeg": "https://pixiv.pximg.net/fanbox/public/images/user/10013868/icon/HQBS5TrKZRZ0gEZrsbmtCX3b.jpeg",
    },
}


@pytest.mark.parametrize(
    "raw_url, normalized_url, expected_class",
    [(raw_url, normalized_url, expected_class) for expected_class, url_groups in urls.items()
     for raw_url, normalized_url in url_groups.items()],
)
def test_parsing(raw_url, normalized_url, expected_class) -> None:
    generate_parsing_test(raw_url=raw_url, normalized_url=normalized_url, expected_class=expected_class)
