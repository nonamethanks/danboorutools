from functools import cached_property
from typing import Literal

from danboorutools.models.url import ArtistUrl, PostUrl, Url


class LineUrl(Url):
    ...


class LineArtistUrl(ArtistUrl, LineUrl):
    artist_id: int
    store: Literal["stickershop", "themeshop"]

    normalize_template = "https://store.line.me/{store}/author/{artist_id}"

    @cached_property
    def is_deleted(self) -> bool:
        if self.html.select("[data-test='author-item']"):
            return False

        if self.html.select("[data-test='no-item-available-text']"):
            return True

        raise NotImplementedError(self)

    @property
    def primary_names(self) -> list[str]:
        if self.is_deleted:
            return []
        raise NotImplementedError(self)

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return []


class LinePostUrl(PostUrl, LineUrl):
    product_id: str
    store: Literal["stickershop", "themeshop"]

    normalize_template = "https://store.line.me/{store}/product/{product_id}"

    @cached_property
    def is_deleted(self) -> bool:
        raise NotImplementedError
        # need to implement logic in case of expired ones, such as https://store.line.me/stickershop/product/1003926/en


class LineMangaAuthorUrl(ArtistUrl, LineUrl):
    author_id: int
    normalize_template = "https://manga.line.me/indies/author/detail?author_id={author_id}"


class LineMusicArtistUrl(ArtistUrl, LineUrl):
    artist_id: str
    normalize_template = "https://music.line.me/webapp/artist/{artist_id}"

    @property
    def primary_names(self) -> list[str]:
        assert (name_el := self.html.select_one(".artist_summary_section .title"))
        return [name_el.text.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return []


class LineMusicAlbumUrl(PostUrl, LineUrl):
    album_id: str
    normalize_template = "https://music.line.me/webapp/album/{album_id}"
