from __future__ import annotations

import os
from datetime import UTC, datetime
from functools import cached_property
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, RedirectUrl, Url, parse_list
from danboorutools.util.misc import extract_urls_from_string

if TYPE_CHECKING:
    from collections.abc import Iterator


class PostypeUrl(Url):
    ...


class PostypeArtistUrl(ArtistUrl, PostypeUrl):
    username: str

    normalize_template = "https://{username}.postype.com"

    @property
    def primary_names(self) -> list[str]:
        assert (name_el := self.html.select_one(".ch-home-author-bio .profile-title"))
        return [name_el.text.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return [self.username]

    @property
    def related(self) -> list[Url]:
        assert (bio_el := self.html.select_one(".author-bio"))
        if not bio_el.select("p"):
            return []
        assert (bio_element := bio_el.select_one("p"))
        return list(map(Url.parse, extract_urls_from_string(bio_element.text)))

    def _extract_assets(self) -> list:
        return []

    def _extract_posts_from_each_page(self) -> Iterator[list[str]]:
        page_template = "https://{username}.postype.com/posts/page/{page_number}"
        page_number = 1
        while True:
            page = self.session.get(page_template.format(username=self.username, page_number=page_number)).html

            yield [post.attrs["href"] for post in page.select(".post-list .post-data-thumbnail > a")]

            page_number += 1

    def _process_post(self, post_object: str) -> None:
        assert isinstance(post := Url.parse(post_object), PostypePostUrl)

        self._register_post(
            post,
            assets=post._extract_assets(),
            created_at=post.created_at,
            score=post.score,
        )

    def subscribe(self) -> None:
        blog_id = self.html.select_one("body").attrs["data-blog-id"]
        resp = self.session.post(
            f"https://api.postype.com/api/v1/subscriber/{blog_id}", cookies={"ps_at": os.environ["POSTYPE_PS_AT_COOKIE"]})
        if resp.status_code == 202:
            return
        raise NotImplementedError(resp.status_code)


class PostypeSeriesUrl(ArtistAlbumUrl, PostypeUrl):
    series_id: int
    username: str

    normalize_template = "https://{username}.postype.com/series/{series_id}"


class PostypePostUrl(PostUrl, PostypeUrl):
    post_id: int
    username: str

    normalize_template = "https://{username}.postype.com/post/{post_id}"

    @cached_property
    def post_data(self) -> BeautifulSoup:
        data = self.session.get(f"https://www.postype.com/api/post/content/{self.post_id}").json()
        return BeautifulSoup(data["data"]["html"], "html.parser")

    def _extract_assets(self) -> list[PostypeImageUrl]:
        els = self.post_data.select(".photoset a")
        return parse_list([el["href"] for el in els], PostypeImageUrl)

    @cached_property
    def score(self) -> int:
        return 0

    @cached_property
    def created_at(self) -> str:
        return min(self._extract_assets(), key=lambda a: a.created_at).created_at

    @cached_property
    def gallery(self) -> list[PostypeArtistUrl]:
        return PostypeArtistUrl.build(username=self.username)


class PostypeBadArtistUrl(RedirectUrl, PostypeUrl):
    user_id: str

    normalize_template = "https://www.postype.com/profile/{user_id}"


class PostypeImageUrl(PostAssetUrl, PostypeUrl):

    @property
    def full_size(self) -> str:
        return self.parsed_url.url_without_query

    @property
    def created_at(self) -> datetime:
        year, month, day, hour, minute = map(int, self.parsed_url.url_parts[:-1])
        return datetime(year=year, month=month, day=day, hour=hour, minute=minute, tzinfo=UTC)
