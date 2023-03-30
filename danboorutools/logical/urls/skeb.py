from __future__ import annotations

import re
from functools import cached_property

from danboorutools.logical.sessions.skeb import SkebArtistData, SkebPostData, SkebSession
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

    score = 0
    created_at = None

    @property
    def post_data(self) -> SkebPostData:
        return self.session.get_post_data(username=self.username, post_id=self.post_id)

    @property
    def gallery(self) -> SkebArtistUrl:
        return SkebArtistUrl.build(username=self.username)

    def _extract_assets(self) -> list[str]:
        if all(file["information"]["extension"] == "pdf" for file in self.post_data.previews):
            return []
        previews = [file["url"] for file in self.post_data.previews]

        if unwatermarked := self.post_data.article_image_url:
            assets = []
            parsed_unwatermarked = Url.parse(unwatermarked)
            assert isinstance(parsed_unwatermarked, SkebImageUrl)
            for preview in previews:
                parsed_preview = Url.parse(preview)
                assert isinstance(parsed_preview, SkebImageUrl)
                if not parsed_preview.image_uuid:  # noqa: SIM114
                    assets.append(preview)
                elif parsed_preview.image_uuid != parsed_unwatermarked.image_uuid:  # noqa: SIM114
                    assets.append(preview)
                elif (match := re.search(r"fm=(\w+)", preview)) and match.groups()[0] in ["gif", "mp4"]:  # noqa: SIM114
                    assets.append(preview)
                elif "&txt=" not in preview:
                    assets.append(preview)
                else:
                    assets.append(unwatermarked)
        else:
            assets = previews
        return assets


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
