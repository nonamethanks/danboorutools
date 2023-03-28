from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from danboorutools.exceptions import DeadUrlError
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url

if TYPE_CHECKING:
    from danboorutools.logical.urls.pixiv import PixivStaccUrl


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
        from danboorutools.logical.urls.pixiv import PixivStaccUrl
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

    @cached_property
    def is_deleted(self) -> bool:
        try:
            # proxies don't like pixiv sketch's 404s for some reason
            response = self.session.head(self.normalized_url, proxies={})
        except DeadUrlError:
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
