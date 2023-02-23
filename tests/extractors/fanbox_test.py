from ward import test

from danboorutools.models.url import Url

urls = {
    "https://www.fanbox.cc/@tsukiori": "https://tsukiori.fanbox.cc",

    "https://omu001.fanbox.cc": "https://omu001.fanbox.cc",
    "https://omu001.fanbox.cc/posts": "https://omu001.fanbox.cc",
    "https://omu001.fanbox.cc/plans": "https://omu001.fanbox.cc",

    "https://downloads.fanbox.cc/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png": "https://downloads.fanbox.cc/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png",
    "https://downloads.fanbox.cc/images/post/39714/c/1200x630/JvjJal8v1yLgc5DPyEI05YpT.jpeg": "https://downloads.fanbox.cc/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.jpeg",
    "https://downloads.fanbox.cc/images/post/39714/w/1200/JvjJal8v1yLgc5DPyEI05YpT.jpeg": "https://downloads.fanbox.cc/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.jpeg",

    "https://www.fanbox.cc/@tsukiori/posts/1080657": "https://tsukiori.fanbox.cc/posts/1080657",

    "https://omu001.fanbox.cc/posts/39714": "https://omu001.fanbox.cc/posts/39714",
    "https://brllbrll.fanbox.cc/posts/626093": "https://brllbrll.fanbox.cc/posts/626093",


    "https://pixiv.net/fanbox/creator/1566167/post/39714": "https://www.pixiv.net/fanbox/creator/1566167/post/39714",
    "https://www.pixiv.net/fanbox/creator/1566167/post/39714": "https://www.pixiv.net/fanbox/creator/1566167/post/39714",
    "https://www.pixiv.net/fanbox/entry.php?entry_id=1264": "https://www.pixiv.net/fanbox/entry.php?entry_id=1264",
    "https://pixiv.net/fanbox/creator/1566167": "https://www.pixiv.net/fanbox/creator/1566167",
    "https://www.pixiv.net/fanbox/creator/1566167": "https://www.pixiv.net/fanbox/creator/1566167",
    "https://www.pixiv.net/fanbox/user/3410642": "https://www.pixiv.net/fanbox/creator/3410642",
    "https://www.pixiv.net/fanbox/creator/18915237/post": "https://www.pixiv.net/fanbox/creator/18915237",
    "http://pixiv.net/fanbox/member.php?user_id=3410642": "https://www.pixiv.net/fanbox/creator/3410642",
    "http://www.pixiv.net/fanbox/member.php?user_id=3410642": "https://www.pixiv.net/fanbox/creator/3410642",

    "https://fanbox.pixiv.net/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png": "https://fanbox.pixiv.net/images/post/39714/JvjJal8v1yLgc5DPyEI05YpT.png",
    "https://fanbox.pixiv.net/files/post/207010/y1qrUK90dn63JXqUE21itupM.png": "https://fanbox.pixiv.net/files/post/207010/y1qrUK90dn63JXqUE21itupM.png",


    "https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg": "https://pixiv.pximg.net/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg",
    "https://pixiv.pximg.net/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg": "https://pixiv.pximg.net/fanbox/public/images/post/186919/cover/VCI1Mcs2rbmWPg0mmiTisovn.jpeg",

    "https://pixiv.pximg.net/c/400x400_90_a2_g5/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg": "https://pixiv.pximg.net/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg",
    "https://pixiv.pximg.net/c/1620x580_90_a2_g5/fanbox/public/images/creator/1566167/cover/QqxYtuWdy4XWQx1ZLIqr4wvA.jpeg": "https://pixiv.pximg.net/fanbox/public/images/creator/1566167/cover/QqxYtuWdy4XWQx1ZLIqr4wvA.jpeg",
    "https://pixiv.pximg.net/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg": "https://pixiv.pximg.net/fanbox/public/images/creator/1566167/profile/Ix6bnJmTaOAFZhXHLbWyIY1e.jpeg",
}

for original_string, normalized_string in urls.items():
    parsed_url = Url.parse(original_string)
    domain = parsed_url.parsed_url.domain

    @test(f"Normalizing {domain}: {original_string}", tags=["parsing", "normalization", domain])
    def _(_parsed_url=parsed_url, _normalized_string=normalized_string) -> None:
        assert _parsed_url.normalized_url == _normalized_string
