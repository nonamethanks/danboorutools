from collections.abc import Iterator

from danboorutools.exceptions import NotAnArtistError
from danboorutools.models.url import ArtistUrl, PostUrl, Url


class SubscribestarUrl(Url):
    ...


class SubscribestarArtistUrl(ArtistUrl, SubscribestarUrl):
    username: str

    normalize_template = "https://subscribestar.adult/{username}"

    @property
    def primary_names(self) -> list[str]:
        return [self.username]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return []

    @property
    def inactive_profile(self) -> bool:
        return "profile is under review" in self.html

    def _extract_posts_from_each_page(self) -> Iterator[list]:
        if self.inactive_profile:
            raise NotAnArtistError
        raise NotImplementedError

    def subscribe(self) -> None:
        if self.inactive_profile:
            raise NotAnArtistError


class SubscribestarPostUrl(PostUrl, SubscribestarUrl):
    post_id: int

    normalize_template = "https://subscribestar.adult/posts/{post_id}"
