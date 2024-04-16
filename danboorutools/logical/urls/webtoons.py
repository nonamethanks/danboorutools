from __future__ import annotations

from functools import cached_property

from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostUrl, RedirectUrl, Url


class WebtoonsUrl(Url):
    ...


class WebtoonsArtistUrl(ArtistUrl, WebtoonsUrl):
    language: str
    creator_id: str

    normalize_template = "https://www.webtoons.com/{language}/creator/{creator_id}"

    @property
    def primary_names(self) -> list[str]:
        assert (name_el := self.html.select_one(".author_wrap .info .nickname"))
        return [name_el.text.strip()]

    @property
    def secondary_names(self) -> list[str]:
        return []

    @property
    def related(self) -> list[Url]:
        return []


class WebtoonsArtistNoLanguageUrl(RedirectUrl, WebtoonsUrl):
    creator_id: str

    normalize_template = "https://www.webtoons.com/creator/{creator_id}"


class WebtoonsWebtoonUrl(ArtistAlbumUrl, WebtoonsUrl):
    genre: str
    toon_title: str
    toon_id: int
    language: str

    normalize_template = "https://www.webtoons.com/{language}/{genre}/{toon_title}/list?title_no={toon_id}"

    @cached_property
    def gallery(self) -> WebtoonsArtistUrl:
        assert (author_el := self.html.select_one(".author_area a.author"))
        return WebtoonsArtistUrl.parse_and_assert(author_el.attrs["href"])


class WebtoonsChapterUrl(PostUrl, WebtoonsUrl):
    genre: str
    toon_title: str
    chapter_title: str
    toon_id: int
    chapter_id: int
    language: str

    normalize_template = "https://www.webtoons.com/{language}/{genre}/{toon_title}/{chapter_title}/viewer?title_no={toon_id}&episode_no={chapter_id}"
