from __future__ import annotations

from typing import TYPE_CHECKING

from danboorutools.exceptions import UrlIsDeleted
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url

if TYPE_CHECKING:
    from danboorutools.logical.extractors.pixiv import PixivStaccUrl


class PixivSketchUrl(Url):
    pass


class PixivSketchPostUrl(PostUrl, PixivSketchUrl):
    post_id: int

    normalize_template = "https://sketch.pixiv.net/items/{post_id}"


class PixivSketchArtistUrl(ArtistUrl, PixivSketchUrl):
    stacc: str

    normalize_template = "https://sketch.pixiv.net/@{stacc}"

    @property
    def stacc_url(self) -> PixivStaccUrl:
        # pylint: disable=import-outside-toplevel
        from danboorutools.logical.extractors.pixiv import PixivStaccUrl
        return self.build(PixivStaccUrl, stacc=self.stacc)

    @property
    def related(self) -> list[Url]:
        return [self.stacc_url]

    @property
    def primary_names(self) -> list[str]:
        return []

    @property
    def secondary_names(self) -> list[str]:
        return [self.stacc]

    @property
    def is_deleted(self) -> bool:
        try:
            response = self.session.head_cached(self.normalized_url, proxies={})  # proxies don't like pixiv sketch's 404s for some reason
        except UrlIsDeleted:
            return True
        else:
            if response.status_code != 200:
                raise NotImplementedError(self)
            return False


class PixivSketchImageUrl(PostAssetUrl, PixivSketchUrl):
    @property
    def full_size(self) -> str:
        url_parts = self.parsed_url.url_parts
        return f"https://img-sketch.pixiv.net/uploads/medium/file/{url_parts[-2]}/{url_parts[-1]}"
