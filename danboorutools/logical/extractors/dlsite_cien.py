from functools import cached_property

from danboorutools.models.url import ArtistUrl, PostUrl, RedirectUrl, Url


class DlsiteCienUrl(Url):
    ...


class DlsiteCienArticleUrl(PostUrl, DlsiteCienUrl):
    article_id: int
    creator_id: int

    normalize_template = "https://ci-en.dlsite.com/creator/{creator_id}/article/{article_id}"


class DlsiteCienCreatorUrl(ArtistUrl, DlsiteCienUrl):
    normalize_template = "https://ci-en.dlsite.com/creator/{creator_id}"
    creator_id: int


class DlsiteCienProfileUrl(RedirectUrl, DlsiteCienUrl):
    profile_id: int
    normalize_template = "https://ci-en.dlsite.com/profile/{profile_id}"

    @cached_property
    def resolved(self) -> Url:
        raise NotImplementedError


# class DlsiteCienAssetUrl(PostAssetUrl, DlsiteCienUrl):
#     # https://media.ci-en.jp/private/attachment/creator/00003894/be1e514f3ca5cbc4a99a4a0b46e2c5e68247a4c14766ccfc2b003aaefa6a355e/image-web.jpg?px-time=1677786066&px-hash=bcd15448d18832d58835e7f53a93fb3162309a48
#     # https://media.ci-en.jp/private/attachment/creator/00003894/be1e514f3ca5cbc4a99a4a0b46e2c5e68247a4c14766ccfc2b003aaefa6a355e/image-800.jpg?px-time=1677786066&px-hash=bcd15448d18832d58835e7f53a93fb3162309a48
#     # https://media.ci-en.jp/private/attachment/creator/00003894/2b5aad10ad38eb4e7a27992b5730ecd744e0cf986140449ed6c9f33ab7cabc48/video-web.mp4?px-time=1677786066&px-hash=c711a0b728bc39ff2cfb6761e8075a7c4e6d836a
#     # https://media.ci-en.jp/private/attachment/creator/00003894/b563ba4dff0cf184d4a19576bad6d6893958451fbd83b0eb2d53aa326fc9b96e/image-800.jpg?px-time=1677786156&px-hash=5f7a59ed3cd9c8f5a3cdcaf9913466b9704782ad
