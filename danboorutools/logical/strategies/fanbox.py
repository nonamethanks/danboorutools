from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class FanboxUrl(Url):
    pass


class FanboxPostUrl(PostUrl, FanboxUrl):
    normalization = "https://{username}.fanbox.cc/posts/{post_id}"

    username: str
    post_id: int


class FanboxArtistUrl(ArtistUrl, FanboxUrl):
    normalization = "https://{username}.fanbox.cc"

    username: str


class FanboxOldPostUrl(RedirectUrl, FanboxUrl):
    normalization = "https://www.pixiv.net/fanbox/creator/{pixiv_id}/post/{post_id}"

    pixiv_id: int | None
    post_id: int


class FanboxOldArtistUrl(RedirectUrl, FanboxUrl):
    normalization = "https://www.pixiv.net/fanbox/creator/{pixiv_id}"

    # TODO: implement related pixiv -> fanbox and fanbox -> pixiv

    pixiv_id: int


class FanboxArtistImageUrl(PostAssetUrl, FanboxUrl):
    pixiv_id: int
    filename: str
    image_type: str


class FanboxImageUrl(PostAssetUrl, FanboxUrl):
    # https://null.fanbox.cc/39714 TODO: use this to get the post
    post_id: int | None
    pixiv_id: int | None
    filename: str
    image_type: str
