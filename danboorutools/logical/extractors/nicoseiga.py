from __future__ import annotations

from functools import cached_property
from typing import Literal
from urllib.parse import urljoin

from danboorutools.logical.sessions.nicovideo import NicoseigaArtistData, NicovideoSession
from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, Url


class NicoSeigaUrl(Url):
    session = NicovideoSession()


class NicoSeigaIllustUrl(PostUrl, NicoSeigaUrl):
    illust_id: int

    normalize_string = "https://seiga.nicovideo.jp/seiga/im{illust_id}"


class NicoSeigaMangaUrl(PostUrl, NicoSeigaUrl):
    manga_id: int

    normalize_string = "https://seiga.nicovideo.jp/watch/mg{manga_id}"


class NicoSeigaComicUrl(ArtistAlbumUrl, NicoSeigaUrl):
    comic_id: int | str

    normalize_string = "https://seiga.nicovideo.jp/comic/{comic_id}"

    @cached_property
    def gallery(self) -> NicoSeigaArtistUrl:
        user_url = self.html.select_one(".author .name a")["href"]
        parsed = Url.parse(urljoin("https://seiga.nicovideo.jp/", user_url))
        assert isinstance(parsed, NicoSeigaArtistUrl), parsed
        return parsed


class NicoSeigaArtistUrl(ArtistUrl, NicoSeigaUrl):
    user_id: int

    normalize_string = "https://seiga.nicovideo.jp/user/illust/{user_id}"

    @property
    def related(self) -> list[Url]:
        return self.artist_data.related_urls
        # I don't add nicovideo urls here because they're useless most times if gotten from nicoseiga

    @property
    def primary_names(self) -> list[str]:
        return [self.artist_data.nickname]

    @property
    def secondary_names(self) -> list[str]:
        return [f"nicovideo {self.user_id}"]

    @cached_property
    def artist_data(self) -> NicoseigaArtistData:
        return self.session.nicoseiga_artist_data(self.user_id)


class NicoSeigaImageUrl(PostAssetUrl, NicoSeigaUrl):
    image_id: int
    image_type: Literal["manga", "illust"] | None
    # TODO: when getting full filename, compare timestamp and dont recompute if it's still viable

    @property
    def full_size(self) -> str:
        return f"https://seiga.nicovideo.jp/image/source/{self.image_id}"
