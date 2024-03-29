from functools import cached_property
from typing import Literal

from danboorutools.logical.urls.twitter import TwitterArtistUrl
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url


class PrivatterUrl(Url):
    pass


class PrivatterArtistUrl(ArtistUrl, PrivatterUrl):
    username: str

    normalize_template = "https://privatter.net/u/{username}"

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        return [TwitterArtistUrl.build(username=self.username)]


class PrivatterPostUrl(PostUrl, PrivatterUrl):
    post_id: int
    post_type: Literal["p", "i"]  # i seem to be login required to view

    normalize_template = "https://privatter.net/{post_type}/{post_id}"

    @cached_property
    def gallery(self) -> PrivatterArtistUrl:
        username_el = self.html.select_one("#right .panel-default a.panel-title")
        assert username_el
        username = username_el.text.strip()
        if not username.startswith("@"):
            raise NotImplementedError(self, username)
        return PrivatterArtistUrl.build(username=username.removeprefix("@"))


class PrivatterImageUrl(PostAssetUrl, PrivatterUrl):
    @property
    def full_size(self) -> str:
        return self.parsed_url.raw_url
