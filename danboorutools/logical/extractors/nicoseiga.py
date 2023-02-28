from typing import Literal

from danboorutools.models.url import ArtistAlbumUrl, ArtistUrl, PostAssetUrl, PostUrl, Url


class NicoSeigaUrl(Url):
    pass


class NicoSeigaIllustUrl(PostUrl, NicoSeigaUrl):
    illust_id: int

    normalize_string = "https://seiga.nicovideo.jp/seiga/im{illust_id}"


class NicoSeigaMangaUrl(PostUrl, NicoSeigaUrl):
    manga_id: int

    normalize_string = "https://seiga.nicovideo.jp/watch/mg{manga_id}"


class NicoSeigaComicUrl(ArtistAlbumUrl, NicoSeigaUrl):
    comic_id: int | str

    normalize_string = "https://seiga.nicovideo.jp/comic/{comic_id}"


class NicoSeigaArtistUrl(ArtistUrl, NicoSeigaUrl):
    user_id: int

    normalize_string = "https://seiga.nicovideo.jp/user/illust/{user_id}"


class NicoSeigaImageUrl(PostAssetUrl, NicoSeigaUrl):
    image_id: int
    image_type: Literal["manga", "illust"] | None
    # TODO: when getting full filename, compare timestamp and dont recompute if it's still viable

    @property
    def full_size(self) -> str:
        return f"https://seiga.nicovideo.jp/image/source/{self.image_id}"
