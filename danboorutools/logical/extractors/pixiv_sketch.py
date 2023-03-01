from __future__ import annotations

from typing import TYPE_CHECKING

from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url

if TYPE_CHECKING:
    from danboorutools.logical.extractors.pixiv import PixivStaccUrl


class PixivSketchUrl(Url):
    pass


class PixivSketchPostUrl(PostUrl, PixivSketchUrl):
    post_id: int

    normalize_string = "https://sketch.pixiv.net/items/{post_id}"


class PixivSketchArtistUrl(ArtistUrl, PixivSketchUrl):
    stacc: str

    normalize_string = "https://sketch.pixiv.net/@{stacc}"

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
        # pylint: disable=import-outside-toplevel
        from danboorutools.logical.extractors.pixiv import PixivArtistUrl

        pixiv_url = self.stacc_url.me_from_stacc.resolved
        assert isinstance(pixiv_url, PixivArtistUrl)
        return pixiv_url.primary_names

    @property
    def secondary_names(self) -> list[str]:
        return [self.stacc]


class PixivSketchImageUrl(PostAssetUrl, PixivSketchUrl):
    @property
    def full_size(self) -> str:
        url_parts = self.parsed_url.url_parts
        return f"https://img-sketch.pixiv.net/uploads/medium/file/{url_parts[-2]}/{url_parts[-1]}"
