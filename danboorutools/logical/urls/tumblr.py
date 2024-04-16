
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from danboorutools.logical.sessions.tumblr import TumblrBlogData, TumblrPostData, TumblrSession
from danboorutools.models.url import ArtistUrl, GalleryAssetUrl, PostAssetUrl, PostUrl, Url, parse_list

if TYPE_CHECKING:
    from collections.abc import Iterator


class TumblrUrl(Url):
    session = TumblrSession()


class TumblrPostUrl(PostUrl, TumblrUrl):
    post_id: int
    blog_name: str

    normalize_template = "https://{blog_name}.tumblr.com/post/{post_id}"


class TumblrArtistUrl(ArtistUrl, TumblrUrl):
    blog_name: str

    normalize_template = "https://{blog_name}.tumblr.com"

    @property
    def artist_data(self) -> TumblrBlogData:
        return self.session.blog_data(self.blog_name)

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.title]

    @property
    def secondary_names(self) -> list[str]:
        return [self.blog_name]

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls

    def subscribe(self) -> None:
        self.session.subscribe(self.blog_name)

    def unsubscribe(self) -> None:
        self.session.unsubscribe(self.blog_name)

    def _extract_posts_from_each_page(self) -> Iterator[list[TumblrPostData]]:
        offset = 0
        while True:
            posts = self.session.get_posts(blog_name=self.blog_name, offset=offset)
            yield posts
            offset += len(posts)

    def _process_post(self, post_object: TumblrPostData) -> None:
        if post_object.reblogged_root_name:
            return

        post = TumblrPostUrl.build(blog_name=post_object.blog_name, post_id=post_object.id)
        post.gallery = self

        self._register_post(
            post=post,
            assets=post_object.assets,
            score=post_object.note_count,
            created_at=post_object.timestamp,
        )

    def _extract_assets(self) -> list[TumblrStaticImageUrl]:
        return parse_list([self.artist_data.avatar_url, self.artist_data.header_url], TumblrStaticImageUrl)


class TumblrStaticImageUrl(GalleryAssetUrl, TumblrUrl):
    @property
    def full_size(self) -> str:
        return re.sub(r"_\d{,4}\.(\w+)$", r"_512.\1", self.parsed_url.raw_url)


class TumblrImageUrl(PostAssetUrl, TumblrUrl):
    dimensions_pattern = re.compile(r"s\d+x\d+(?:_c\d)?")

    @property
    def full_size(self) -> str:
        if self.dimensions_pattern.search(self.parsed_url.raw_url):
            img = re.sub(rf"\/{self.dimensions_pattern.pattern}\/", "/s21000x21000/", self.parsed_url.raw_url)
        else:
            img = re.sub(r"_\d{,4}\.(\w+)$", r"_1280.\1", self.parsed_url.raw_url)

        return re.sub(r".pnj$", r".png", img)
