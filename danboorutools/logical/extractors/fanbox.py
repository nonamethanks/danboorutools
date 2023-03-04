import re

from danboorutools.logical.sessions.fanbox import FanboxArtistData, FanboxSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class FanboxUrl(Url):
    session = FanboxSession()


class FanboxPostUrl(PostUrl, FanboxUrl):
    username: str
    post_id: int

    normalize_string = "https://{username}.fanbox.cc/posts/{post_id}"


class FanboxArtistUrl(ArtistUrl, FanboxUrl):
    username: str  # it's not guaranteed that this is the stacc. it might change.

    normalize_string = "https://{username}.fanbox.cc"

    @property
    def _artist_data(self) -> FanboxArtistData:
        return self.session.artist_data(self.username)

    @property
    def related(self) -> list[Url]:
        return self._artist_data.related_urls

    @property
    def primary_names(self) -> list[str]:
        return [self._artist_data.user.name]

    @property
    def secondary_names(self) -> list[str]:
        return [self._artist_data.creatorId]


class FanboxOldPostUrl(RedirectUrl, FanboxUrl):
    pixiv_id: int
    post_id: int

    normalize_string = "https://www.pixiv.net/fanbox/creator/{pixiv_id}/post/{post_id}"


class FanboxOldArtistUrl(RedirectUrl, FanboxUrl):

    # TODO: implement related pixiv -> fanbox and fanbox -> pixiv

    pixiv_id: int

    normalize_string = "https://www.pixiv.net/fanbox/creator/{pixiv_id}"


class FanboxArtistImageUrl(PostAssetUrl, FanboxUrl):
    pixiv_id: int
    filename: str
    image_type: str

    @property
    def full_size(self) -> str:
        return re.sub(r"\/[cw]\/\w+\/", "/", self.parsed_url.raw_url)


class FanboxImageUrl(PostAssetUrl, FanboxUrl):
    # https://null.fanbox.cc/39714 TODO: use this to get the post -> dont assign directly, first fetch to check if alive
    post_id: int | None
    pixiv_id: int | None
    filename: str
    image_type: str

    @property
    def full_size(self) -> str:
        return re.sub(r"\/[cw]\/\w+\/", "/", self.parsed_url.raw_url)
