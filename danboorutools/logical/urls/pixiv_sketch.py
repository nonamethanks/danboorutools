from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from danboorutools.exceptions import DeadUrlError
from danboorutools.logical.sessions.pixiv_sketch import PixivSketchPostData, PixivSketchSession
from danboorutools.models.url import ArtistUrl, PostAssetUrl, PostUrl, Url

if TYPE_CHECKING:
    from collections.abc import Iterator

    from danboorutools.logical.feeds.pixiv_sketch import PixivSketchFeed
    from danboorutools.logical.urls.pixiv import PixivStaccUrl


class PixivSketchUrl(Url):
    session = PixivSketchSession()


def _process_post(self: PixivSketchArtistUrl | PixivSketchFeed, post_object: PixivSketchPostData) -> None:
    post = PixivSketchPostUrl.build(post_id=post_object.id)
    post.gallery = PixivSketchArtistUrl.build(stacc=post_object.user.unique_name)

    if not post_object.media:
        return

    assets = [i["photo"]["original"]["url"] for i in post_object.media]

    self._register_post(
        post=post,
        assets=assets,
        created_at=post_object.created_at,
        score=post_object.feedback_count,
    )


class PixivSketchArtistUrl(ArtistUrl, PixivSketchUrl):
    stacc: str

    normalize_template = "https://sketch.pixiv.net/@{stacc}"

    def _extract_posts_from_each_page(self) -> Iterator[list[PixivSketchPostData]]:
        page_url = f"https://sketch.pixiv.net/api/walls/@{self.stacc}/posts/public.json"
        while True:
            page = self.session.get_page_of_posts(
                page_url,
                headers={"x-requested-with": "https://sketch.pixiv.net/"},
            )
            yield page.posts
            if page.next_page:
                page_url = page.next_page
            else:
                return

    _process_post = _process_post

    def _extract_assets(self) -> list:
        # not worth it, most times same as pixiv
        return []

    @property
    def stacc_url(self) -> PixivStaccUrl:
        from danboorutools.logical.urls.pixiv import PixivStaccUrl
        return PixivStaccUrl.build(stacc=self.stacc)

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

    def subscribe(self) -> None:
        self.session.subscribe(self.stacc)


class PixivSketchPostUrl(PostUrl, PixivSketchUrl):
    post_id: int

    normalize_template = "https://sketch.pixiv.net/items/{post_id}"


class PixivSketchImageUrl(PostAssetUrl, PixivSketchUrl):
    @property
    def full_size(self) -> str:
        url_parts = self.parsed_url.url_parts
        return f"https://img-sketch.pixiv.net/uploads/medium/file/{url_parts[-2]}/{url_parts[-1]}"
