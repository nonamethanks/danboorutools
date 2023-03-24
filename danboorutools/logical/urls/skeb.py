from functools import cached_property

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions.skeb import SkebArtistData, SkebSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class SkebUrl(Url):
    session = SkebSession()


class SkebAbsolutePostUrl(RedirectUrl, SkebUrl):
    absolute_post_id: int

    normalize_template = "https://skeb.jp/works/{absolute_post_id}"


class SkebPostUrl(PostUrl, SkebUrl):
    post_id: int
    username: str

    normalize_template = "https://skeb.jp/@{username}/works/{post_id}"


class SkebArtistUrl(ArtistUrl, SkebUrl):
    username: str

    normalize_template = "https://skeb.jp/@{username}"

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.name]

    @property
    def secondary_names(self) -> list[str]:
        return [self.artist_data.screen_name]

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls

    @property
    def artist_data(self) -> SkebArtistData:
        return self.session.artist_data(self.username)


class SkebImageUrl(PostAssetUrl, SkebUrl):
    image_uuid: str | None
    page: int | None
    post_id: int | None

    @cached_property
    def full_size(self) -> str:
        return self.parsed_url.raw_url
