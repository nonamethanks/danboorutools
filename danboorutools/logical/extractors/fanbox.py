import re

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class FanboxUrl(Url):
    pass


class FanboxPostUrl(PostUrl, FanboxUrl):
    username: str
    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        username = kwargs["username"]
        post_id = kwargs["post_id"]
        return f"https://{username}.fanbox.cc/posts/{post_id}"


class FanboxArtistUrl(ArtistUrl, FanboxUrl):
    username: str

    @classmethod
    def normalize(cls, **kwargs) -> str:
        username = kwargs["username"]
        return f"https://{username}.fanbox.cc"


class FanboxOldPostUrl(RedirectUrl, FanboxUrl):
    pixiv_id: int
    post_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        pixiv_id: int | None = kwargs.get("pixiv_id")
        post_id = kwargs["post_id"]
        return f"https://www.pixiv.net/fanbox/creator/{pixiv_id}/post/{post_id}"


class FanboxOldArtistUrl(RedirectUrl, FanboxUrl):

    # TODO: implement related pixiv -> fanbox and fanbox -> pixiv

    pixiv_id: int

    @classmethod
    def normalize(cls, **kwargs) -> str:
        pixiv_id = kwargs["pixiv_id"]
        return f"https://www.pixiv.net/fanbox/creator/{pixiv_id}"


class FanboxArtistImageUrl(PostAssetUrl, FanboxUrl):
    pixiv_id: int
    filename: str
    image_type: str

    @property
    def full_size(self) -> str:
        return re.sub(r"\/[cw]\/\w+\/", "/", self.parsed_url.raw_url)


class FanboxImageUrl(PostAssetUrl, FanboxUrl):
    # https://null.fanbox.cc/39714 TODO: use this to get the post
    post_id: int | None
    pixiv_id: int | None
    filename: str
    image_type: str

    @property
    def full_size(self) -> str:
        return re.sub(r"\/[cw]\/\w+\/", "/", self.parsed_url.raw_url)
