from functools import cached_property

from danboorutools.exceptions import UrlIsDeleted
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url


class SkebUrl(Url):
    pass


class SkebAbsolutePostUrl(RedirectUrl, SkebUrl):
    absolute_post_id: int

    normalize_string = "https://skeb.jp/works/{absolute_post_id}"


class SkebPostUrl(PostUrl, SkebUrl):
    post_id: int
    username: str

    normalize_string = "https://skeb.jp/@{username}/works/{post_id}"


class SkebArtistUrl(ArtistUrl, SkebUrl):
    username: str

    normalize_string = "https://skeb.jp/@{username}"

    @cached_property
    def is_deleted(self) -> bool:
        try:
            self.html  # TODO: redo with the api call maybe? idk
        except UrlIsDeleted:
            return True

        if self.html.select(f".hero img[alt='{self.username}']"):
            return False
        else:
            raise NotImplementedError(self.html)


class SkebImageUrl(PostAssetUrl, SkebUrl):
    image_uuid: str | None
    page: int | None
    post_id: int | None

    @cached_property
    def full_size(self) -> str:
        return self.parsed_url.raw_url
