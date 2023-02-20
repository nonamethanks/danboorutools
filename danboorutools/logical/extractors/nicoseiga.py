from typing import Literal

from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, Url


class NicoSeigaUrl(Url):
    pass


class NicoSeigaIllustUrl(PostUrl, NicoSeigaUrl):
    illust_id: int


class NicoSeigaMangaUrl(PostUrl, NicoSeigaUrl):
    manga_id: int


class NicoSeigaComicUrl(ArtistAlbumUrl, NicoSeigaUrl):
    comic_id: int | str


class NicoSeigaArtistUrl(ArtistUrl, NicoSeigaUrl):
    user_id: int


class NicoSeigaImageUrl(PostAssetUrl, NicoSeigaUrl):
    image_id: int
    image_type: Literal["manga", "illust"] | None
    # TODO: when getting full filename, compare timestamp and dont recompute if it's still viable
